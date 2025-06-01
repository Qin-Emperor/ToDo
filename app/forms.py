from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, EmailField, SubmitField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms.validators import DataRequired, Email


class RegistrationForm(FlaskForm):
    username = StringField("Ім'я користувача:",
                           render_kw={"placeholder": "Введіть ваше ім'я"},
                           validators=[DataRequired()])
    email = EmailField("Електронна пошта:",
                       render_kw={"placeholder": "Введіть вашу пошту"},
                       validators=[DataRequired(), Email()])
    password = PasswordField("Пароль:",
                             render_kw={"placeholder": "Введіть ваш пароль"},
                             validators=[DataRequired()])
    timezone = HiddenField()
    submit = SubmitField("Зареєструватися",
                         render_kw={"onclick": "getTimezone()"})


class LoginForm(FlaskForm):
    email = EmailField("Електронна пошта:",
                       render_kw={"placeholder": "Введіть вашу пошту"},
                       validators=[DataRequired(), Email()])
    password = PasswordField("Пароль:",
                             render_kw={"placeholder": "Введіть ваш пароль"},
                             validators=[DataRequired()])
    submit = SubmitField("Увійти")


class AddTaskForm(FlaskForm):
    content = StringField(render_kw={"placeholder": "Введіть ваше завдання",
                                     "class": "form-control large-input"},
                          validators=[DataRequired()])
    deadline = DateTimeLocalField(validators=[DataRequired()],
                                  render_kw={"class": "form-control small-input"})
    submit = SubmitField("Додати", render_kw={"class": "btn btn-add"})


class UpdateTaskForm(FlaskForm):
    content = StringField(render_kw={"class": "form-control large-input"},
                          validators=[DataRequired()])
    deadline = DateTimeLocalField(validators=[DataRequired()],
                                  render_kw={"class": "form-control small-input"})
    submit = SubmitField("Зберегти", render_kw={"class": "btn btn-save"})
