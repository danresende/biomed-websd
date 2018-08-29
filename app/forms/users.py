from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from config import Config

DEPARTAMENTOS = Config.DEPARTAMENTOS

class UserForm(FlaskForm):
    uid = StringField('UID')
    nome = StringField('Nome', validators=[DataRequired(), Length(min=3, max=20)])
    sobrenome = StringField('Sobrenome', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    departamento = SelectField('Departamento', choices=DEPARTAMENTOS, validators=[DataRequired()])
    representante = BooleanField('Responsável do departamento')
    dba = BooleanField('DBA')
    diretor = BooleanField('Diretor')
    submit = SubmitField('Enviar')
