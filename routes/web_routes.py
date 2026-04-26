from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

web_bp = Blueprint("web", __name__)


def login_required(func):
    """
    Protege as páginas internas.
    Se não houver usuário na sessão, volta para o login.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("web.login"))

        return func(*args, **kwargs)

    return wrapper


@web_bp.route("/")
def index():
    """
    Página inicial do sistema.
    Se estiver logado, vai para o dashboard.
    Se não estiver, vai para o login.
    """

    if "usuario" in session:
        return redirect(url_for("web.dashboard"))

    return redirect(url_for("web.login"))


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login provisório apenas para testar a navegação.

    Depois vamos substituir essa parte por Firebase Auth.
    """

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")

        if not nome or not email:
            flash("Informe nome e e-mail para continuar.", "danger")
            return redirect(url_for("web.login"))

        session["usuario"] = {
            "nome": nome,
            "email": email
        }

        flash(f"Bem-vindo, {nome}!", "success")
        return redirect(url_for("web.dashboard"))

    return render_template("login/loginPage.html")


@web_bp.route("/sobre")
def sobre():
    return render_template("login/aboutPage.html")


@web_bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("web.login"))


@web_bp.route("/menu/dashboard")
@login_required
def dashboard():
    return render_template("menu/dashboardPage.html")


@web_bp.route("/menu/configuracoes")
@login_required
def configuracoes():
    return render_template("menu/configuracoesPage.html")


@web_bp.route("/menu/alimentos")
@login_required
def alimento_list():
    alimentos = [
        {
            "id": "1",
            "nome": "Arroz",
            "categoria": "Cereal",
            "unidade": "kg"
        },
        {
            "id": "2",
            "nome": "Feijão",
            "categoria": "Leguminosa",
            "unidade": "kg"
        }
    ]

    return render_template(
        "menu/alimentos/alimentoListPage.html",
        alimentos=alimentos
    )


@web_bp.route("/menu/alimentos/adicionar", methods=["GET", "POST"])
@login_required
def alimento_add():
    if request.method == "POST":
        nome = request.form.get("nome")
        categoria = request.form.get("categoria")
        unidade = request.form.get("unidade")

        print("Novo alimento recebido:")
        print("Nome:", nome)
        print("Categoria:", categoria)
        print("Unidade:", unidade)

        flash("Alimento cadastrado temporariamente.", "success")
        return redirect(url_for("web.alimento_list"))

    return render_template("menu/alimentos/alimentoAddPage.html")


@web_bp.route("/menu/alimentos/editar/<alimento_id>", methods=["GET", "POST"])
@login_required
def alimento_edit(alimento_id):
    alimento = {
        "id": alimento_id,
        "nome": "Arroz",
        "categoria": "Cereal",
        "unidade": "kg"
    }

    if request.method == "POST":
        nome = request.form.get("nome")
        categoria = request.form.get("categoria")
        unidade = request.form.get("unidade")

        print("Alimento editado:")
        print("ID:", alimento_id)
        print("Nome:", nome)
        print("Categoria:", categoria)
        print("Unidade:", unidade)

        flash("Alimento atualizado temporariamente.", "success")
        return redirect(url_for("web.alimento_list"))

    return render_template(
        "menu/alimentos/alimentoEditPage.html",
        alimento=alimento
    )


@web_bp.route("/menu/usuarios")
@login_required
def usuario_list():
    usuarios = [
        {
            "id": "1",
            "nome": "Regis",
            "email": "regis@email.com"
        }
    ]

    return render_template(
        "menu/usuarios/usuarioListPage.html",
        usuarios=usuarios
    )


@web_bp.route("/menu/usuarios/editar/<usuario_id>", methods=["GET", "POST"])
@login_required
def usuario_edit(usuario_id):
    usuario = {
        "id": usuario_id,
        "nome": session["usuario"]["nome"],
        "email": session["usuario"]["email"]
    }

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")

        print("Usuário editado:")
        print("ID:", usuario_id)
        print("Nome:", nome)
        print("Email:", email)

        session["usuario"] = {
            "nome": nome,
            "email": email
        }

        flash("Usuário atualizado temporariamente.", "success")
        return redirect(url_for("web.usuario_list"))

    return render_template(
        "menu/usuarios/usuarioEditPage.html",
        usuario=usuario
    )