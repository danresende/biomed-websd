from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (DateField, DecimalField, SelectField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Length, Optional

from config import Config

EMPRESA = Config.EMPRESA
DEPARTAMENTOS = Config.DEPARTAMENTOS
FORMA_PGTO = Config.FORMA_PGTO
TIPO_SOLICITACAO = Config.TIPO_SOLICITACAO


class FlexibleDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(",", "."))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Not a valid float value"))


class DespesaForm(FlaskForm):
    empresa = SelectField("Empresa", choices=EMPRESA, validators=[DataRequired()])
    centro_custo = StringField(
        "Centro de custo (não esqueça dos pontos):", validators=[DataRequired()]
    )
    data_pagamento = DateField("Vencimento: ", validators=[DataRequired()])
    departamento = SelectField(
        "Departamento:", choices=DEPARTAMENTOS, validators=[DataRequired()]
    )
    fornecedor = StringField("Fornecedor", validators=[DataRequired()])
    descricao = TextAreaField(
        "Descrição:", validators=[Length(min=10, max=280), DataRequired()]
    )
    forma_pagamento = SelectField(
        "Forma de pagamento:", choices=FORMA_PGTO, validators=[DataRequired()]
    )
    observacao = TextAreaField("Observação:", validators=[Optional(), Length(max=280)])
    tipo_solicitacao = SelectField(
        "Tipo de solicitação:", choices=TIPO_SOLICITACAO, validators=[DataRequired()]
    )
    valor_total = FlexibleDecimalField(
        "Valor total (somente números):", validators=[DataRequired()]
    )
    previsao = StringField(
        "Número da previsão (caso haja):", validators=[Optional(), Length(max=14)]
    )
    boleto = FileField(
        "Em caso de boleto, anexe aqui o arquivo (apenas PDF!):",
        validators=[FileAllowed(["pdf"], "Apenas PDF!")],
    )
    submit = SubmitField("Enviar")


class MotivoDesaprovForm(FlaskForm):
    motivo = TextAreaField(
        "Motivo:", validators=[Length(min=10, max=280), DataRequired()]
    )
    submit = SubmitField("Enviar")
