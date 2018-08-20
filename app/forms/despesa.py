from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, DateField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed
from config import Config

DEPARTAMENTOS = Config.DEPARTAMENTOS
FORMA_PGTO = Config.FORMA_PGTO
TIPO_SOLICITACAO = Config.TIPO_SOLICITACAO

class FlexibleDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))

class DespesaForm(FlaskForm):
    centro_custo = StringField('Centro de custo (não esqueça dos pontos):', validators=[DataRequired()])
    data_pagamento = DateField('Vencimento: ', format='%d/%m/%Y', validators=[DataRequired()])
    departamento = SelectField('Departamento:', choices=DEPARTAMENTOS, validators=[DataRequired()])
    descricao = TextAreaField('Descrição:', validators=[Length(min=10, max=280), DataRequired()])
    forma_pagamento = SelectField('Forma de pagamento:', choices=FORMA_PGTO, validators=[DataRequired()])
    observacao = TextAreaField('Observação:', validators=[Optional(), Length(max=280)])
    tipo_solicitacao = SelectField('Tipo de solicitação:', choices=TIPO_SOLICITACAO, validators=[DataRequired()])
    valor_total = FlexibleDecimalField('Valor total (somente números):', validators=[DataRequired()])
    boleto = FileField('Em caso de boleto faça upload do arquivo (apenas PDF!):', validators=[FileAllowed(['pdf'], 'Apenas PDF!')])
    submit = SubmitField('Enviar')

