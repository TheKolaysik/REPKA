from flask import Flask, redirect, render_template, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import requests

from data import db_session, comp_api
from data.users import User
from data.news import News
from forms.news import NewsForm, ProjectForm, CommentForm, CityForm
from data.components import Components
from data.comments import Comment
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

organization = None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Главная
@app.route("/", methods=["GET", "POST"])
def index():
    form = CityForm()
    global organization
    if form.validate_on_submit():
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        search_params = {
            "apikey": api_key,
            "text": f"Радиодетали, {form.title.data}",
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params)
        if not response:
            return render_template("start_page.html", form=form)
        # Преобразуем ответ в json-объект
        store_dic = {}
        json_response = response.json()
        organization = json_response["features"]
        for i in range(len(organization)):
            store_dic[i] = store_dic.get(i, organization[i])
        for i, t in store_dic.items():
            print(i, t)
        return render_template('shops.html', shops=store_dic)
        # return redirect("/projects")
    return render_template("start_page.html", form=form)


# Проекты
@app.route("/projects", methods=['GET', 'POST'])
def projects():
    db_sess = db_session.create_session()
    form = ProjectForm()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.is_private != True) | (News.user == current_user))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    if form.validate_on_submit():
        if form.is_private.data:
            news = db_sess.query(News).filter(News.user == current_user)
    return render_template("index.html", news=news, form=form)


# Отображение магазина
@app.route("/shop/<int:id>", methods=['GET', 'POST'])
def shop(id):
    global organization
    shop_n = organization[id]
    coords = shop_n['geometry']['coordinates']
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={coords[0]},{coords[1]}&spn=0.002,0.002&l=map&pt={coords[0]},{coords[1]},comma"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Запишем полученное изображение в файл.
    map_file = "static/img/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return render_template('shop.html', shop=shop_n)


# Страница публикации
@app.route("/project/<int:id>", methods=['GET', 'POST'])
def project(id):
    form = CommentForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        comments = Comment(content=form.comment.data, news_id=id)
        current_user.comments.append(comments)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/project/{id}')
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            News.id == id, News.user == current_user).first()
    else:
        news = db_sess.query(News).filter(
            News.id == id, News.is_private != True).first()
    if news is None:
        news = db_sess.query(News).filter(
            News.id == id, News.is_private != True).first()
    if news:
        comments = db_sess.query(Comment).filter((news.id == Comment.news_id))
        return render_template("project.html", news=news, comments=comments, form=form)
    return redirect("/projects")


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data, about=form.about.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# Авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/projects")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/projects")


# Таблица с радиокомпонентами
@app.route('/components')
def components():
    db_sess = db_session.create_session()
    comps = db_sess.query(Components).all()
    return render_template("components.html", comps=comps, title='Радиокомпоненты')


# Добавление публикации
@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.about = form.url.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/projects')
    return render_template('news.html', title='Добавление проекта', form=form)


# Удаление публикации
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/projects')


# Редактирование публикации
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.about = form.url.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect(f'/project/{id}')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование проекта',
                           form=form
                           )


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(comp_api.blueprint)
    app.run()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
