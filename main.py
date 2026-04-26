from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import check_password_hash
import os

from database import criar_usuario_inicial, buscar_usuario_por_username

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave_temporaria")


criar_usuario_inicial()


def login_obrigatorio(funcao):
    """
    Decorador para proteger páginas.
    Se o usuário não estiver logado, volta para o login.
    """

    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        senha = request.form.get("senha")

        usuario = buscar_usuario_por_username(username)

        if usuario and usuario.get("ativo") and check_password_hash(usuario["senha_hash"], senha):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_perfil"] = usuario["perfil"]

            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("dashboard"))

        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login/loginPage.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


@app.route("/sobre")
def sobre():
    return render_template("login/aboutPage.html")


@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    return render_template("menu/dashboardPage.html")


@app.route("/menu")
@login_obrigatorio
def menu():
    return render_template("menu/dashboardPage.html")


if __name__ == "__main__":
    app.run(debug=True)