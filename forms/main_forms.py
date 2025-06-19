from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, FloatField, SelectField
from wtforms.validators import InputRequired
 
class UploadForm(FlaskForm):
    file = FileField("Качи CSV файл", validators=[InputRequired()])
    submit = SubmitField("Качи")
 
class TrainModelForm(FlaskForm):
    model_type = SelectField("Избери модел", choices=[('linear', 'Линейна регресия'), ('logistic', 'Логистична регресия')])
    test_size = FloatField("Размер на тестовия сет (например 0.2)", default=0.2)
    submit = SubmitField("Обучи")