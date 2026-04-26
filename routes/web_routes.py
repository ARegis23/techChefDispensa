from functools import wraps
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    send_file
)

from services.auth_service import verificar_token_firebase

from services.usuario_service import (
    garantir_usuario_logado,
    listar_usuarios_da_conta,
    buscar_usuario_por_uid,
    criar_usuario_membro,
    atualizar_usuario,
    deletar_usuario,
    pode_editar_usuario,
    pode_deletar_usuario,
    buscar_preferencias_acessibilidade,
    atualizar_preferencias_acessibilidade
)

from services.open_food_facts_service import buscar_alimento_por_barcode_api

from services.alimento_service import (
    listar_alimentos,
    buscar_alimento,
    criar_alimento,
    atualizar_alimento,
    deletar_alimento,
    montar_dados_alimento
)

from services.export_service import gerar_json_exportacao

from services.importacao_service import (
    listar_importacoes,
    buscar_importacao,
    importar_por_barcode,
    montar_dados_importacao_formulario,
    atualizar_importacao,
    deletar_importacao,
    marcar_importacao_enviada_para_alimentos
)

web_bp = Blueprint("web", __name__)

# Decorador para proteger rotas que exigem autenticação
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

# Rotas para autenticação e páginas públicas
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


@web_bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("web.login"))

# Rotas para dashboard e páginas informativas
@web_bp.route("/menu/dashboard")
@login_required
def dashboard():
    return render_template("menu/dashboardPage.html")

@web_bp.route("/sobre")
def sobre():
    return render_template("login/aboutPage.html")


# Rotas para gerenciamento de configurações e preferências
@web_bp.route("/menu/configuracoes", methods=["GET", "POST"])
@login_required
def configuracoes():
    usuario_logado = session.get("usuario")
    uid = usuario_logado.get("uid")

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "salvar_acessibilidade":
            try:
                dados = {
                    "tema": request.form.get("tema"),
                    "tamanho_texto": request.form.get("tamanho_texto"),
                    "contraste": request.form.get("contraste"),
                    "reduzir_animacoes": request.form.get("reduzir_animacoes"),
                    "densidade_interface": request.form.get("densidade_interface"),
                    "fonte_legivel": request.form.get("fonte_legivel")
                }

                preferencias = atualizar_preferencias_acessibilidade(uid, dados)

                session["usuario"]["acessibilidade"] = preferencias

                flash("Preferências de acessibilidade atualizadas com sucesso.", "success")
                return redirect(url_for("web.configuracoes"))

            except Exception as erro:
                print("Erro ao atualizar acessibilidade:", erro)
                flash("Não foi possível salvar as preferências de acessibilidade.", "danger")
                return redirect(url_for("web.configuracoes"))

    preferencias = buscar_preferencias_acessibilidade(uid)

    return render_template(
        "menu/configuracoesPage.html",
        preferencias=preferencias,
        usuario_logado=usuario_logado
    )


# Rotas para gerenciamento de alimentos
@web_bp.route("/menu/alimentos")
@login_required
def alimento_list():
    usuario_logado = session.get("usuario")

    alimentos = listar_alimentos(usuario_logado)

    return render_template(
        "menu/alimentos/alimentoListPage.html",
        alimentos=alimentos
    )


@web_bp.route("/menu/alimentos/tabela")
@login_required
def alimento_tabela():
    usuario_logado = session.get("usuario")

    alimentos = listar_alimentos(usuario_logado)

    return render_template(
        "menu/alimentos/alimentoTablePage.html",
        alimentos=alimentos
    )


@web_bp.route("/menu/alimentos/adicionar", methods=["GET", "POST"])
@login_required
def alimento_add():
    usuario_logado = session.get("usuario")

    alimento_api = None
    barcode_consultado = request.args.get("barcode", "").strip()

    if request.method == "GET" and barcode_consultado:
        alimento_api = buscar_alimento_por_barcode_api(barcode_consultado)

        if alimento_api:
            flash("Dados encontrados na API. Confira e complete o que faltar.", "success")
        else:
            flash("Produto não encontrado na API. Preencha os dados manualmente.", "warning")
            alimento_api = {
                "barcode": barcode_consultado,
                "nome": "",
                "marca": "",
                "categoria": "",
                "peso": "",
                "alergenos": "",
                "kcal": "",
                "carboidratos": "",
                "proteinas": "",
                "fibras": "",
                "sodio": "",
                "gorduras_totais": "",
                "gorduras_saturadas": "",
                "gorduras_trans": "",
                "acucares_totais": "",
                "acucares_adicionados": "",
                "origem_dados": "manual"
            }

    if request.method == "POST":
        try:
            dados_alimento = montar_dados_alimento(request.form, usuario_logado)

            if not dados_alimento.get("barcode"):
                flash("O código de barras é obrigatório.", "danger")
                return redirect(url_for("web.alimento_add"))

            if not dados_alimento.get("nome"):
                flash("O nome do alimento é obrigatório.", "danger")
                return redirect(url_for("web.alimento_add"))

            criar_alimento(usuario_logado, dados_alimento)

            flash("Alimento cadastrado com sucesso.", "success")
            return redirect(url_for("web.alimento_list"))

        except ValueError as erro:
            flash(str(erro), "danger")
            return redirect(url_for("web.alimento_add"))

        except Exception as erro:
            print("Erro ao cadastrar alimento:", erro)
            flash("Não foi possível cadastrar o alimento.", "danger")
            return redirect(url_for("web.alimento_add"))

    return render_template(
        "menu/alimentos/alimentoAddPage.html",
        alimento=alimento_api
    )

@web_bp.route("/menu/alimentos/editar/<barcode>", methods=["GET", "POST"])
@login_required
def alimento_edit(barcode):
    usuario_logado = session.get("usuario")

    alimento = buscar_alimento(usuario_logado, barcode)

    if not alimento:
        flash("Alimento não encontrado.", "danger")
        return redirect(url_for("web.alimento_list"))

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "cancelar":
            return redirect(url_for("web.alimento_list"))

        if acao == "deletar":
            try:
                deletar_alimento(usuario_logado, barcode)
                flash("Alimento deletado com sucesso.", "success")
                return redirect(url_for("web.alimento_list"))

            except Exception as erro:
                print("Erro ao deletar alimento:", erro)
                flash("Não foi possível deletar o alimento.", "danger")
                return redirect(url_for("web.alimento_edit", barcode=barcode))

        try:
            dados_alimento = montar_dados_alimento(request.form, usuario_logado)

            if not dados_alimento.get("nome"):
                flash("O nome do alimento é obrigatório.", "danger")
                return redirect(url_for("web.alimento_edit", barcode=barcode))

            atualizar_alimento(usuario_logado, barcode, dados_alimento)

            flash("Alimento atualizado com sucesso.", "success")
            return redirect(url_for("web.alimento_list"))

        except Exception as erro:
            print("Erro ao atualizar alimento:", erro)
            flash("Não foi possível atualizar o alimento.", "danger")
            return redirect(url_for("web.alimento_edit", barcode=barcode))

    return render_template(
        "menu/alimentos/alimentoEditPage.html",
        alimento=alimento
    )


# Rotas para gerenciamento de usuários (apenas para administradores)
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

# Rotas para exportação de dados
@web_bp.route("/menu/configuracoes/exportar-json")
@login_required
def exportar_json_zip():
    """
    Exporta os dados do grupo em JSON compactado em ZIP.

    Exporta:
    - usuários vinculados ao admin_uid
    - alimentos cadastrados no grupo
    """

    usuario_logado = session.get("usuario")

    if not usuario_logado:
        flash("Usuário não autenticado.", "danger")
        return redirect(url_for("web.login"))

    # Recomendação: exportação completa apenas para admin.
    # Se quiser liberar para membros também, remova este bloco.
    if usuario_logado.get("papel") != "admin":
        flash("Apenas o administrador pode exportar todos os dados do grupo.", "danger")
        return redirect(url_for("web.configuracoes"))

    try:
        json_exportado = gerar_json_exportacao(usuario_logado)

        memoria_zip = BytesIO()

        data_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_json = f"dados_techchef_{data_arquivo}.json"
        nome_zip = f"exportacao_techchef_{data_arquivo}.zip"

        with ZipFile(memoria_zip, mode="w", compression=ZIP_DEFLATED) as arquivo_zip:
            arquivo_zip.writestr(nome_json, json_exportado)

        memoria_zip.seek(0)

        return send_file(
            memoria_zip,
            mimetype="application/zip",
            as_attachment=True,
            download_name=nome_zip
        )

    except Exception as erro:
        print("Erro ao exportar dados:", erro)
        flash("Não foi possível exportar os dados da aplicação.", "danger")
        return redirect(url_for("web.configuracoes"))
    

 # Rotas para importação de dados

@web_bp.route("/menu/importacoes")
@login_required
def importacao_list():
    usuario_logado = session.get("usuario")

    importacoes = listar_importacoes(usuario_logado)

    return render_template(
        "menu/importacoes/importacaoListPage.html",
        importacoes=importacoes
    )


@web_bp.route("/menu/importacoes/nova", methods=["GET", "POST"])
@login_required
def importacao_add():
    usuario_logado = session.get("usuario")

    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()

        if not barcode:
            flash("Informe o código de barras para importar.", "danger")
            return redirect(url_for("web.importacao_add"))

        try:
            importacao = importar_por_barcode(usuario_logado, barcode)

            if importacao.get("status") == "importado":
                flash("Dados importados com sucesso.", "success")
            else:
                flash("Produto não encontrado na API. Registro criado para revisão manual.", "warning")

            return redirect(url_for("web.importacao_list"))

        except Exception as erro:
            print("Erro ao importar dados:", erro)
            flash("Não foi possível importar os dados.", "danger")
            return redirect(url_for("web.importacao_add"))

    return render_template("menu/importacoes/importacaoAddPage.html")


@web_bp.route("/menu/importacoes/editar/<importacao_id>", methods=["GET", "POST"])
@login_required
def importacao_edit(importacao_id):
    usuario_logado = session.get("usuario")

    importacao = buscar_importacao(usuario_logado, importacao_id)

    if not importacao:
        flash("Importação não encontrada.", "danger")
        return redirect(url_for("web.importacao_list"))

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "cancelar":
            return redirect(url_for("web.importacao_list"))

        if acao == "deletar":
            try:
                deletar_importacao(usuario_logado, importacao_id)
                flash("Importação deletada com sucesso.", "success")
                return redirect(url_for("web.importacao_list"))

            except Exception as erro:
                print("Erro ao deletar importação:", erro)
                flash("Não foi possível deletar a importação.", "danger")
                return redirect(url_for("web.importacao_edit", importacao_id=importacao_id))

        try:
            dados_importacao = montar_dados_importacao_formulario(
                request.form,
                usuario_logado
            )

            if not dados_importacao.get("barcode"):
                flash("O código de barras é obrigatório.", "danger")
                return redirect(url_for("web.importacao_edit", importacao_id=importacao_id))

            atualizar_importacao(
                usuario_logado,
                importacao_id,
                dados_importacao
            )

            flash("Importação atualizada com sucesso.", "success")
            return redirect(url_for("web.importacao_list"))

        except Exception as erro:
            print("Erro ao atualizar importação:", erro)
            flash("Não foi possível atualizar a importação.", "danger")
            return redirect(url_for("web.importacao_edit", importacao_id=importacao_id))

    return render_template(
        "menu/importacoes/importacaoEditPage.html",
        importacao=importacao
    )


@web_bp.route("/menu/importacoes/enviar-para-alimentos/<importacao_id>", methods=["POST"])
@login_required
def importacao_enviar_para_alimentos(importacao_id):
    usuario_logado = session.get("usuario")

    importacao = buscar_importacao(usuario_logado, importacao_id)

    if not importacao:
        flash("Importação não encontrada.", "danger")
        return redirect(url_for("web.importacao_list"))

    try:
        dados_alimento = {
            "barcode": importacao.get("barcode"),
            "nome": importacao.get("nome"),
            "marca": importacao.get("marca"),
            "categoria": importacao.get("categoria"),
            "peso": importacao.get("peso"),
            "alergenos": importacao.get("alergenos"),

            "kcal": importacao.get("kcal"),
            "carboidratos": importacao.get("carboidratos"),
            "proteinas": importacao.get("proteinas"),
            "fibras": importacao.get("fibras"),
            "sodio": importacao.get("sodio"),
            "gorduras_totais": importacao.get("gorduras_totais"),
            "gorduras_saturadas": importacao.get("gorduras_saturadas"),
            "gorduras_trans": importacao.get("gorduras_trans"),
            "acucares_totais": importacao.get("acucares_totais"),
            "acucares_adicionados": importacao.get("acucares_adicionados"),

            "origem_dados": "importacao",
            "admin_uid": usuario_logado.get("admin_uid"),
            "atualizado_por": usuario_logado.get("uid"),
            "atualizado_por_nome": usuario_logado.get("nome")
        }

        alimento_existente = buscar_alimento(
            usuario_logado,
            dados_alimento.get("barcode")
        )

        if alimento_existente:
            atualizar_alimento(
                usuario_logado,
                dados_alimento.get("barcode"),
                dados_alimento
            )
            flash("Alimento atualizado com base na importação.", "success")
        else:
            criar_alimento(usuario_logado, dados_alimento)
            flash("Alimento cadastrado com base na importação.", "success")

        marcar_importacao_enviada_para_alimentos(
            usuario_logado,
            importacao_id
        )

        return redirect(url_for("web.alimento_list"))

    except Exception as erro:
        print("Erro ao enviar importação para alimentos:", erro)
        flash("Não foi possível enviar a importação para alimentos.", "danger")
        return redirect(url_for("web.importacao_edit", importacao_id=importacao_id))   
    
@web_bp.route("/menu/importacoes/deletar/<importacao_id>", methods=["POST"])
@login_required
def importacao_delete(importacao_id):
    usuario_logado = session.get("usuario")

    try:
        deletar_importacao(usuario_logado, importacao_id)

        flash("Importação deletada com sucesso.", "success")
        return redirect(url_for("web.importacao_list"))

    except Exception as erro:
        print("Erro ao deletar importação:", erro)

        flash("Não foi possível deletar a importação.", "danger")
        return redirect(url_for("web.importacao_list"))