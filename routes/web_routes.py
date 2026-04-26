from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from services.auth_service import verificar_token_firebase
from services.usuario_service import garantir_usuario_logado
from services.usuario_service import (
    listar_usuarios_da_conta,
    buscar_usuario_por_uid,
    criar_usuario_membro,
    atualizar_usuario,
    deletar_usuario,
    pode_editar_usuario,
    pode_deletar_usuario
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
    if "usuario" in session:
        return redirect(url_for("web.dashboard"))

    return redirect(url_for("web.login"))


@web_bp.route("/login", methods=["GET"])
def login():
    if "usuario" in session:
        return redirect(url_for("web.dashboard"))

    return render_template("login/loginPage.html")


@web_bp.route("/auth/session-login", methods=["POST"])
def session_login():
    """
    Recebe o ID Token do Firebase, valida no backend
    e cria a sessão Flask.
    """

    try:
        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({
                "ok": False,
                "erro": "Dados da requisição não foram enviados corretamente."
            }), 400

        id_token = dados.get("idToken")

        if not id_token:
            return jsonify({
                "ok": False,
                "erro": "Token de autenticação não enviado."
            }), 400

        usuario = verificar_token_firebase(id_token)

        if not usuario.get("uid"):
            return jsonify({
                "ok": False,
                "erro": "Usuário inválido."
            }), 401

        usuario_firestore = garantir_usuario_logado(usuario)

        session["usuario"] = {
            "uid": usuario_firestore.get("uid"),
            "nome": usuario_firestore.get("nome"),
            "email": usuario_firestore.get("email"),
            "foto": usuario_firestore.get("foto"),
            "papel": usuario_firestore.get("papel"),
            "admin_uid": usuario_firestore.get("admin_uid")
        }

        return jsonify({
            "ok": True,
            "redirect": url_for("web.dashboard")
        })

    except ValueError as erro:
        print("Token malformado:", erro)

        return jsonify({
            "ok": False,
            "erro": "Token inválido."
        }), 401

    except Exception as erro:
        print("Erro ao validar autenticação:", erro)

        return jsonify({
            "ok": False,
            "erro": "Não foi possível validar sua autenticação. Tente entrar novamente."
        }), 401


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
    usuario_logado = session.get("usuario")

    admin, membros = listar_usuarios_da_conta(usuario_logado)

    return render_template(
        "menu/usuarios/usuarioListPage.html",
        admin=admin,
        membros=membros,
        usuario_logado=usuario_logado
    )


@web_bp.route("/menu/usuarios/adicionar", methods=["GET", "POST"])
@login_required
def usuario_add():
    usuario_logado = session.get("usuario")

    if usuario_logado.get("papel") != "admin":
        flash("Apenas o administrador pode adicionar usuários.", "danger")
        return redirect(url_for("web.usuario_list"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Informe nome, e-mail e senha.", "danger")
            return redirect(url_for("web.usuario_add"))

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return redirect(url_for("web.usuario_add"))

        try:
            criar_usuario_membro(usuario_logado, nome, email, senha)

            flash("Usuário adicionado com sucesso.", "success")
            return redirect(url_for("web.usuario_list"))

        except Exception as erro:
            print("Erro ao criar usuário:", erro)
            flash("Não foi possível criar o usuário. Verifique os dados informados.", "danger")
            return redirect(url_for("web.usuario_add"))

    return render_template("menu/usuarios/usuarioAddPage.html")


@web_bp.route("/menu/usuarios/editar/<uid>", methods=["GET", "POST"])
@login_required
def usuario_edit(uid):
    usuario_logado = session.get("usuario")

    if not pode_editar_usuario(usuario_logado, uid):
        flash("Você só pode editar o seu próprio cadastro.", "danger")
        return redirect(url_for("web.usuario_list"))

    usuario = buscar_usuario_por_uid(uid)

    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("web.usuario_list"))

    if usuario.get("admin_uid") != usuario_logado.get("admin_uid"):
        flash("Usuário não pertence à sua conta.", "danger")
        return redirect(url_for("web.usuario_list"))

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "cancelar":
            return redirect(url_for("web.usuario_list"))

        if acao == "deletar":
            if not pode_deletar_usuario(usuario_logado, uid):
                flash("Você não tem permissão para deletar este usuário.", "danger")
                return redirect(url_for("web.usuario_edit", uid=uid))

            try:
                deletar_usuario(usuario_logado, uid)
                flash("Usuário deletado com sucesso.", "success")
                return redirect(url_for("web.usuario_list"))

            except Exception as erro:
                print("Erro ao deletar usuário:", erro)
                flash("Não foi possível deletar o usuário.", "danger")
                return redirect(url_for("web.usuario_edit", uid=uid))

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
            return redirect(url_for("web.usuario_edit", uid=uid))

        if senha and len(senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.", "danger")
            return redirect(url_for("web.usuario_edit", uid=uid))

        try:
            usuario_atualizado = atualizar_usuario(
                usuario_logado=usuario_logado,
                uid_alvo=uid,
                nome=nome,
                email=email,
                senha=senha if senha else None
            )

            if usuario_logado.get("uid") == uid:
                session["usuario"]["nome"] = usuario_atualizado.get("nome")
                session["usuario"]["email"] = usuario_atualizado.get("email")

            flash("Usuário atualizado com sucesso.", "success")
            return redirect(url_for("web.usuario_list"))

        except Exception as erro:
            print("Erro ao atualizar usuário:", erro)
            flash("Não foi possível atualizar o usuário.", "danger")
            return redirect(url_for("web.usuario_edit", uid=uid))

    pode_deletar = pode_deletar_usuario(usuario_logado, uid)

    return render_template(
        "menu/usuarios/usuarioEditPage.html",
        usuario=usuario,
        usuario_logado=usuario_logado,
        pode_deletar=pode_deletar
    )