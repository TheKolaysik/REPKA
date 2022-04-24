from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, URLField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    url = URLField("Ссылка")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class ProjectForm(FlaskForm):
    is_private = BooleanField("Отобразить только мои")
    submit = SubmitField("Применить")


class CommentForm(FlaskForm):
    comment = TextAreaField("Добавить комментарий")
    submit = SubmitField('Добавить')


class CityForm(FlaskForm):
    title = StringField('Город')
    submit = SubmitField("Применить")
