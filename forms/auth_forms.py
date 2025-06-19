from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo
 
class LoginForm(FlaskForm):
    email = StringField("Имейл", validators=[InputRequired(), Email()])
    password = PasswordField("Парола", validators=[InputRequired()])
    submit = SubmitField("Вход")
 
class RegisterForm(FlaskForm):
    username = StringField("Потребителско име", validators=[InputRequired(), Length(min=3, max=25)])
    email = StringField("Имейл", validators=[InputRequired(), Email()])
    password = PasswordField("Парола", validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField("Потвърди парола", validators=[InputRequired(), EqualTo('password')])
    role = SelectField("Роля", choices=[('student', 'Ученик'), ('admin', 'Администратор')])
    submit = SubmitField("Регистрация")