from flask import Flask, redirect, render_template, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session, comp_api
from data.users import User
from data.news import News
from forms.news import NewsForm, ProjectForm
from data.components import Components
from data.comments import Comment
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("start_page.html", news=news)


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


@app.route("/project/<int:id>", methods=['GET', 'POST'])
def project(id):
    db_sess = db_session.create_session()
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
        comments = db_sess.query(Comment).filter((News.id == Comment.news_id))
        return render_template("project.html", news=news, comments=comments)
    return redirect("/projects")


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


@app.route('/components')
def components():
    db_sess = db_session.create_session()
    comps = db_sess.query(Components).all()
    return render_template("components.html", comps=comps, title='Радиокомпоненты')


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


if __name__ == '__main__':
    main()
