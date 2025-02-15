import json

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.forms import LoginForm
from app.modules import User
from firebase import auth

Login = Blueprint("login", __name__)


# Login/Logout
################################################################################


# Login
@Login.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("despesas.listar"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = auth.sign_in_with_email_and_password(
                form.email.data, form.password.data
            )
            user = User(user["localId"], user["idToken"], user["refreshToken"])
            login_user(user)
            return redirect(url_for("despesas.listar"))
        except Exception as e:
            current_app.logger.error(f"Usuário {form.email.data} não conseguiu acessar o sistema.\nErro do programa:\n{e}")
            mensagem = json.loads(e.strerror)["error"]["message"]
            mensagem = mensagem.replace("_", " ")
            flash(mensagem)
            return redirect(url_for("login.login"))
    return render_template("login/login.html", form=form)


# Logout
@Login.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login.login"))


# Reset password
@Login.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["user_email"]
        auth.send_password_reset_email(email)
        return redirect(url_for("login.login"))
    else:
        return render_template("login/reset_password.html")
