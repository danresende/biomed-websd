import os
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from numpy import busday_count
from werkzeug.utils import secure_filename

from app.forms import DespesaForm, MotivoDesaprovForm
from config import Config
from emailfunc import send_mail
from firebase import db, storage

Despesas = Blueprint("despesas", __name__)

# Funções auxiliares
################################################################################


def teste_politica_pgto(despesa):

    valor_pgto = float(despesa["valor_total"])
    data_pgto = datetime.strptime(despesa["data_pagamento"], "%d/%m/%Y")
    hoje = datetime.now()
    delta = data_pgto - hoje
    delta = delta.days + 1

    mensagem = "Este pagamento está fora da política de pagamentos. Por favor, verifique se o motivo da urgência está descrito."

    if valor_pgto > 5000 and delta < 20:
        flash(mensagem)
    elif valor_pgto > 2500 and delta < 10:
        flash(mensagem)
    elif valor_pgto > 250 and delta < 5:
        flash(mensagem)
    elif valor_pgto <= 250 and delta < 2:
        flash(mensagem)

    return None


def teste_tempo_inclusao(despesa, target):

    data_pgto = datetime.strptime(despesa["data_pagamento"], "%d/%m/%Y")
    hoje = datetime.now()
    wd_delta = busday_count(hoje.strftime("%Y-%m-%d"), data_pgto.strftime("%Y-%m-%d"))

    if wd_delta <= target:
        flash(
            "Esta SD está com vencimento menor do que o necessário de inclusão para pagamento (2 dias úteis). Por favor, verifique se a data está correta ou o motivo da urgência está descrito."
        )

    print(wd_delta)
    print(target)

    return None


def teste_vencimento_valido(despesa):
    data_pagamento = datetime.strptime(despesa["data_pagamento"], "%d/%m/%Y")
    if data_pagamento > datetime.today():
        return True
    else:
        return False


FORMA_PGTO = dict(Config.FORMA_PGTO)
TIPO_SOLICITACAO = dict(Config.TIPO_SOLICITACAO)


# Despesas
################################################################################


# Listar
@Despesas.route("/")
@login_required
def listar():
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    usuario = db.child("users").child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    data = {}
    try:
        data = db.child("despesas").get(current_user.idToken)
        data = dict(data.val())

    except Exception as e:
        data = {}
        print(e)

    despesas = []
    for k, v in data.items():
        despesa = v
        despesa["id"] = k
        despesa["data_criacao"] = datetime.strptime(despesa["data_criacao"], "%d/%m/%Y")
        despesa["data_pagamento"] = datetime.strptime(
            despesa["data_pagamento"], "%d/%m/%Y"
        )
        despesa["data_ult_alt"] = datetime.strptime(despesa["data_ult_alt"], "%d/%m/%Y")

        delta = datetime.now() - despesa["data_ult_alt"]

        if despesa["status"] >= "4" and delta.days > 120:
            continue

        despesas.append(despesa)

    despesas = sorted(despesas, key=lambda k: k["id"], reverse=True)

    depto_usuario = current_user.departamento

    if depto_usuario == "financeiro":
        return render_template(
            "despesas/listar.html", despesas=despesas, is_dba=usuario["DBA"]
        )

    elif current_user.departamento == "administrativo":
        despesas = [
            despesa
            for despesa in despesas
            if (
                despesa["departamento"] == depto_usuario
                or despesa["departamento"] == "estoque"
                or despesa["criado_por"] == current_user.email
            )
        ]
        return render_template(
            "despesas/listar.html", despesas=despesas, is_dba=usuario["DBA"]
        )

    else:
        despesas = [
            despesa
            for despesa in despesas
            if (
                despesa["departamento"] == depto_usuario
                or despesa["criado_por"] == current_user.email
            )
        ]
        return render_template(
            "despesas/listar.html", despesas=despesas, is_dba=usuario["DBA"]
        )


# Criar
@Despesas.route("/criar", methods=["GET", "POST"])
@login_required
def criar():
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    form = DespesaForm()
    if form.validate_on_submit():
        despesa = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "centro_custo": form.centro_custo.data,
            "criado_por": current_user.email,
            "modificado_por": current_user.email,
            "data_criacao": datetime.now().strftime("%d/%m/%Y"),
            "data_pagamento": form.data_pagamento.data.strftime("%d/%m/%Y"),
            "data_ult_alt": datetime.now().strftime("%d/%m/%Y"),
            "departamento": form.departamento.data,
            "descricao": form.descricao.data,
            "empresa": form.empresa.data,
            "fornecedor": form.fornecedor.data,
            "forma_pagamento": form.forma_pagamento.data,
            "previsao": form.previsao.data,
            "observacao": form.observacao.data,
            "tipo_solicitacao": form.tipo_solicitacao.data,
            "valor_total": "{:.2f}".format(form.valor_total.data),
            "status": "1",
            "tem_arquivo": False,
        }

        if form.boleto.data is not None:
            despesa["tem_arquivo"] = True
            boleto = os.path.join("/tmp", secure_filename(form.boleto.data.filename))
            form.boleto.data.save(boleto)

        if despesa["departamento"] == "diretoria":
            despesa["status"] = "2"

        try:
            if form.boleto.data is not None:
                response = storage.child("boletos/" + despesa["id"]).put(
                    boleto, current_user.idToken
                )
                despesa["download_token"] = response["downloadTokens"]
            db.child("despesas").child(despesa["id"]).update(
                despesa, current_user.idToken
            )
            send_mail(despesa, current_user)
            return redirect(url_for("despesas.listar"))

        except Exception as e:
            mensagem = "Não foi possível incluir essa despesa."
            print(e)
            flash(mensagem)
            return redirect(url_for("despesas.criar"))

    return render_template("despesas/criar.html", form=form)


# Detalhar
@Despesas.route("/detalhar/<id>")
@login_required
def detalhar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    usuario = db.child("users").child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())
    despesa["id"] = id

    if despesa["status"] == "2":
        teste_tempo_inclusao(despesa, 0)
    elif despesa["status"] == "1":
        teste_tempo_inclusao(despesa, 1)

    if despesa["status"] <= "3" and despesa["tipo_solicitacao"] != "50":
        if "previsao" not in despesa.keys():
            teste_politica_pgto(despesa)
        elif despesa["previsao"] == "":
            teste_politica_pgto(despesa)

    if despesa["tem_arquivo"]:
        try:
            arquivo_url = storage.child("boletos/" + id).get_url(
                despesa["download_token"]
            )
        except Exception as e:
            print(e)
    else:
        arquivo_url = "#"

    despesa["forma_pagamento"] = FORMA_PGTO[despesa["forma_pagamento"]]
    despesa["tipo_solicitacao"] = TIPO_SOLICITACAO[despesa["tipo_solicitacao"]]

    if usuario["RD"]:

        if current_user.departamento == despesa["departamento"]:
            pode_aprovar = True
        elif (
            current_user.departamento == "administrativo"
            and despesa["departamento"] == "estoque"
        ):
            pode_aprovar = True
        else:
            pode_aprovar = False

    else:
        pode_aprovar = False

    vencimento_valido = teste_vencimento_valido(despesa)

    return render_template(
        "despesas/detalhar.html",
        despesa=despesa,
        usuario=usuario,
        download=arquivo_url,
        pode_aprovar=pode_aprovar,
        vencimento_valido=vencimento_valido,
    )


# Editar
@Despesas.route("/editar/<id>", methods=["GET", "POST"])
@login_required
def editar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())
    despesa["id"] = id

    if "previsao" not in despesa.keys():
        despesa["previsao"] = ""

    form = DespesaForm()
    if form.validate_on_submit():
        despesa = {
            "centro_custo": form.centro_custo.data,
            "modificado_por": current_user.email,
            "data_pagamento": form.data_pagamento.data.strftime("%d/%m/%Y"),
            "data_ult_alt": datetime.now().strftime("%d/%m/%Y"),
            "departamento": form.departamento.data,
            "descricao": form.descricao.data,
            "empresa": form.empresa.data,
            "fornecedor": form.fornecedor.data,
            "forma_pagamento": form.forma_pagamento.data,
            "observacao": form.observacao.data,
            "tipo_solicitacao": form.tipo_solicitacao.data,
            "valor_total": "{:.2f}".format(form.valor_total.data),
            "previsao": form.previsao.data,
            "status": "1",
        }

        if form.boleto.data is not None:
            despesa["tem_arquivo"] = True
            boleto = os.path.join("/tmp", secure_filename(form.boleto.data.filename))
            form.boleto.data.save(boleto)

        try:
            despesa["modificado_por"] = current_user.email
            despesa["data_ult_alt"] = datetime.now().strftime("%d/%m/%Y")
            if form.boleto.data is not None:
                response = storage.child("boletos/" + id).put(
                    boleto, current_user.idToken
                )
                despesa["download_token"] = response["downloadTokens"]
            db.child("despesas").child(id).update(despesa, current_user.idToken)
            send_mail(despesa, current_user)
            return redirect(url_for("despesas.listar"))

        except Exception as e:
            mensagem = "Não foi possível atualizar essa despesa."
            print(e)
            flash(mensagem)

        return redirect(url_for("despesas.detalhar", id=id))

    elif request.method == "GET":
        form.centro_custo.data = despesa["centro_custo"]
        form.data_pagamento.data = datetime.strptime(
            despesa["data_pagamento"], "%d/%m/%Y"
        )
        form.departamento.data = despesa["departamento"]
        form.descricao.data = despesa["descricao"]
        form.empresa.data = despesa["empresa"]
        form.fornecedor.data = despesa["fornecedor"]
        form.forma_pagamento.data = despesa["forma_pagamento"]
        form.previsao.data = despesa["previsao"]
        form.observacao.data = despesa["observacao"]
        form.tipo_solicitacao.data = despesa["tipo_solicitacao"]
        form.valor_total.data = float(despesa["valor_total"])

    return render_template("despesas/editar.html", form=form, despesa=despesa)


# Deletar
@Despesas.route("/deletar/<id>")
@login_required
def deletar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    try:
        if despesa["tem_arquivo"]:
            storage.child("gs://").delete("boletos/" + id)
        db.child("despesas").child(id).remove(current_user.idToken)

    except Exception as e:
        mensagem = "Não foi possível deletar a despesa"
        print(e)
        flash(mensagem)

    return redirect(url_for("despesas.listar"))


# Aprovação
@Despesas.route("/aprovar/<id>")
@login_required
def aprovacao(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    usuario = db.child("users").child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    fin = usuario["departamento"] == "financeiro"

    if usuario["RD"]:
        if current_user.departamento == despesa["departamento"]:
            resp_depto = True
        elif (
            current_user.departamento == "administrativo"
            and despesa["departamento"] == "estoque"
        ):
            resp_depto = True
        else:
            resp_depto = False
    else:
        resp_depto = False

    if usuario["RD"] and fin:
        resp_fin = True
    else:
        resp_fin = False

    if despesa["status"] == "1" and resp_depto:
        despesa["status"] = "2"

    elif despesa["status"] == "2" and resp_fin:
        despesa["status"] = "3"

    elif despesa["status"] == "3" and fin:
        despesa["status"] = "4"

    try:
        despesa["modificado_por"] = current_user.email
        despesa["data_ult_alt"] = datetime.now().strftime("%d/%m/%Y")
        db.child("despesas").child(id).update(despesa, current_user.idToken)
        send_mail(despesa, current_user)

    except Exception as e:
        mensagem = "Não foi possível atualizar essa despesa."
        print(e)
        flash(mensagem)

    return redirect(url_for("despesas.listar"))


# Desaprovação
@Despesas.route("/desaprovar/<id>", methods=["GET", "POST"])
@login_required
def desaprovacao(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    usuario = db.child("users").child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    fin = usuario["departamento"] == "financeiro"

    if usuario["RD"]:
        if current_user.departamento == despesa["departamento"]:
            resp_depto = True
        elif (
            current_user.departamento == "administrativo"
            and despesa["departamento"] == "estoque"
        ):
            resp_depto = True
        else:
            resp_depto = False
    else:
        resp_depto = False

    if usuario["RD"] and fin:
        resp_fin = True
    else:
        resp_fin = False

    form = MotivoDesaprovForm()
    if form.validate_on_submit():
        motivo = form.motivo.data

        if despesa["status"] == "1" and resp_depto:
            despesa["status"] = "5"

        elif despesa["status"] == "2" and resp_fin:
            despesa["status"] = "6"

        try:
            despesa["modificado_por"] = current_user.email
            despesa["data_ult_alt"] = datetime.now().strftime("%d/%m/%Y")
            db.child("despesas").child(id).update(despesa, current_user.idToken)
            send_mail(despesa, current_user, motivo)

        except Exception as e:
            mensagem = "Não foi possível atualizar essa despesa."
            print(e)
            flash(mensagem)

        return redirect(url_for("despesas.listar"))

    return render_template("despesas/desaprovar.html", form=form, despesa=despesa)


# Cancelar
@Despesas.route("/cancelar/<id>")
@login_required
def cancelar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    usuario = db.child("users").child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())

    pode_cancelar = (
        usuario["departamento"] == despesa["departamento"]
        or usuario["email"] == despesa["criado_por"]
    )

    if pode_cancelar and despesa["status"] != "7":
        despesa["status"] = "7"

    try:
        despesa["modificado_por"] = current_user.email
        despesa["data_ult_alt"] = datetime.now().strftime("%d/%m/%Y")
        db.child("despesas").child(id).update(despesa, current_user.idToken)
        send_mail(despesa, current_user)

    except Exception as e:
        mensagem = "Não foi possível atualizar essa despesa."
        print(e)
        flash(mensagem)

    return redirect(url_for("despesas.listar"))


# Efetivar
@Despesas.route("/efetivar/<id>", methods=["GET", "POST"])
@login_required
def efetivar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    despesa = db.child("despesas").child(id).get(current_user.idToken)
    despesa = dict(despesa.val())
    despesa["previsao"] = id
    despesa["tipo_solicitacao"] = "04"

    form = DespesaForm()
    if form.validate_on_submit():
        despesa = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "centro_custo": form.centro_custo.data,
            "criado_por": current_user.email,
            "modificado_por": current_user.email,
            "data_criacao": datetime.now().strftime("%d/%m/%Y"),
            "data_pagamento": form.data_pagamento.data.strftime("%d/%m/%Y"),
            "data_ult_alt": datetime.now().strftime("%d/%m/%Y"),
            "departamento": form.departamento.data,
            "descricao": form.descricao.data,
            "empresa": form.empresa.data,
            "fornecedor": form.fornecedor.data,
            "forma_pagamento": form.forma_pagamento.data,
            "previsao": form.previsao.data,
            "observacao": form.observacao.data,
            "tipo_solicitacao": form.tipo_solicitacao.data,
            "valor_total": "{:.2f}".format(form.valor_total.data),
            "status": "1",
            "tem_arquivo": False,
        }

        if form.boleto.data is not None:
            despesa["tem_arquivo"] = True
            boleto = os.path.join("/tmp", secure_filename(form.boleto.data.filename))
            form.boleto.data.save(boleto)

        if despesa["departamento"] == "diretoria":
            despesa["status"] = "2"

        try:
            if form.boleto.data is not None:
                response = storage.child("boletos/" + despesa["id"]).put(
                    boleto, current_user.idToken
                )
                despesa["download_token"] = response["downloadTokens"]
            db.child("despesas").child(despesa["id"]).update(
                despesa, current_user.idToken
            )
            send_mail(despesa, current_user)
            return redirect(url_for("despesas.listar"))

        except Exception as e:
            mensagem = "Não foi possível atualizar essa despesa."
            print(e)
            flash(mensagem)

        return redirect(url_for("despesas.detalhar", id=id))

    elif request.method == "GET":
        form.centro_custo.data = despesa["centro_custo"]
        form.data_pagamento.data = datetime.strptime(
            despesa["data_pagamento"], "%d/%m/%Y"
        )
        form.departamento.data = despesa["departamento"]
        form.descricao.data = despesa["descricao"]
        form.empresa.data = despesa["empresa"]
        form.fornecedor.data = despesa["fornecedor"]
        form.forma_pagamento.data = despesa["forma_pagamento"]
        form.previsao.data = despesa["previsao"]
        form.observacao.data = despesa["observacao"]
        form.tipo_solicitacao.data = despesa["tipo_solicitacao"]
        form.valor_total.data = float(despesa["valor_total"])

    return render_template("despesas/efetivar.html", form=form, despesa=despesa)
