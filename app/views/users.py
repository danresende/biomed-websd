from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms import UserForm
from firebase import db

Users = Blueprint("users", __name__)


def verify_dba(current_user):
    usuario = db.child("users").child(current_user.localId).get(current_user.idToken)
    usuario = dict(usuario.val())
    return not usuario["DBA"]


# Usuários
################################################################################


# Listar
@Users.route("/")
@login_required
def listar():
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    if verify_dba(current_user):
        return redirect(url_for("despesas.listar"))

    data = db.child("users").get(current_user.idToken)
    data = dict(data.val())

    usuarios = []
    for k, v in data.items():
        usuario = v
        usuario["id"] = k
        usuarios.append(usuario)

    usuarios = sorted(usuarios, key=lambda k: (k["departamento"], k["nome"]))

    return render_template("users/listar.html", usuarios=usuarios)


# Criar
@Users.route("/criar", methods=["GET", "POST"])
@login_required
def criar():
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    if verify_dba(current_user):
        return redirect(url_for("despesas.listar"))

    form = UserForm()
    if form.validate_on_submit():
        uid = form.uid.data
        usuario = {
            "nome": form.nome.data,
            "sobrenome": form.sobrenome.data,
            "email": form.email.data,
            "departamento": form.departamento.data,
            "RD": form.representante.data,
            "DBA": form.dba.data,
            "Diretor": form.diretor.data,
        }

        try:
            db.child("users").child(uid).update(usuario, current_user.idToken)
            return redirect(url_for("users.listar"))

        except Exception as e:
            mensagem = "Não foi possível incluir este usuário."
            print(e)
            flash(mensagem)
            return redirect(url_for("users.criar"))

    return render_template("users/criar.html", form=form)


# Detalhar
@Users.route("/detalhar/<id>")
@login_required
def detalhar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    if verify_dba(current_user):
        return redirect(url_for("despesas.listar"))

    usuario = db.child("users").child(id).get(current_user.idToken)
    usuario = dict(usuario.val())
    usuario["id"] = id

    return render_template("users/detalhar.html", usuario=usuario)


# Editar
@Users.route("/editar/<id>", methods=["GET", "POST"])
@login_required
def editar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token()

    if verify_dba(current_user):
        return redirect(url_for("despesas.listar"))

    usuario = db.child("users").child(id).get(current_user.idToken)
    usuario = dict(usuario.val())
    usuario["id"] = id

    form = UserForm()
    if form.validate_on_submit():
        usuario = {
            "nome": form.nome.data,
            "sobrenome": form.sobrenome.data,
            "email": form.email.data,
            "departamento": form.departamento.data,
            "RD": form.representante.data,
            "DBA": form.dba.data,
            "Diretor": form.diretor.data,
        }

        print(usuario)
        try:
            db.child("users").child(id).update(usuario, current_user.idToken)

        except Exception as e:
            mensagem = "Não for possível atualizar os dados deste usuário."
            print(e)
            flash(mensagem)

        return redirect(url_for("users.detalhar", id=id))

    elif request.method == "GET":
        form.nome.data = usuario["nome"]
        form.sobrenome.data = usuario["sobrenome"]
        form.email.data = usuario["email"]
        form.departamento.data = usuario["departamento"]
        form.representante.data = usuario["RD"]
        form.dba.data = usuario["DBA"]
        form.diretor.data = usuario["Diretor"]

    return render_template("users/editar.html", form=form, usuario=usuario)


# Deletar
@Users.route("deletar/<id>", methods=["GET", "POST"])
@login_required
def deletar(id):
    if current_user.is_active() and current_user.session_over():
        current_user.reset_token

    if verify_dba(current_user):
        return redirect(url_for("despesas.listar"))

    db.child("users").child(id).remove(current_user.idToken)
    print("deletedo o usuário" + id)

    return redirect(url_for("users.listar"))
