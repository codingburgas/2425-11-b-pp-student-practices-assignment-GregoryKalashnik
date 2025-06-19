from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length
 
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    submit = SubmitField('Вход')
 
class RegisterForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Потвърди парола', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Роля', choices=[('student', 'Ученик'), ('teacher', 'Учител'), ('admin', 'Админ')], validators=[DataRequired()])
    submit = SubmitField('Регистрация')
 
class UploadForm(FlaskForm):
    file = FileField('Качи CSV файл', validators=[DataRequired()])
    submit = SubmitField('Качи')
 
class TrainModelForm(FlaskForm):
    model_type = SelectField('Избери модел', choices=[
        ('linear', 'Линейна регресия'),
        ('logistic', 'Логистична регресия'),
        ('neural', 'Невронна мрежа')
    ])
    test_size = FloatField('Размер на тестовия сет (напр. 0.2)', default=0.2)
    submit = SubmitField('Обучи')