from firebase_admin import auth
from google.cloud import firestore

from config.firebase_config import iniciar_firebase


db = iniciar_firebase()


def buscar_usuario_por_uid(uid):
    doc = db.collection("usuarios").document(uid).get()

    if doc.exists:
        return doc.to_dict()

    return None


def garantir_usuario_logado(usuario_sessao):
    """
    Garante que o usuário autenticado exista no Firestore.

    Se ele ainda não existir, ele vira admin da própria conta.
    Isso é útil para o primeiro login do usuário principal.
    """

    uid = usuario_sessao.get("uid")

    if not uid:
        return None

    usuario_existente = buscar_usuario_por_uid(uid)

    if usuario_existente:
        return usuario_existente

    novo_usuario = {
        "uid": uid,
        "nome": usuario_sessao.get("nome") or "Usuário",
        "email": usuario_sessao.get("email"),
        "foto": usuario_sessao.get("foto"),
        "papel": "admin",
        "admin_uid": uid,
        "ativo": True,
        "criado_em": firestore.SERVER_TIMESTAMP,
        "atualizado_em": firestore.SERVER_TIMESTAMP
    }

    db.collection("usuarios").document(uid).set(novo_usuario)

    return novo_usuario


def obter_admin_uid(usuario_logado):
    """
    Retorna o admin_uid da conta/família do usuário.
    """

    if usuario_logado.get("papel") == "admin":
        return usuario_logado.get("uid")

    return usuario_logado.get("admin_uid")


def listar_usuarios_da_conta(usuario_logado):
    """
    Lista o admin separado dos membros.
    """

    admin_uid = obter_admin_uid(usuario_logado)

    usuarios_ref = (
        db.collection("usuarios")
        .where("admin_uid", "==", admin_uid)
        .where("ativo", "==", True)
        .stream()
    )

    admin = None
    membros = []

    for doc in usuarios_ref:
        usuario = doc.to_dict()

        if usuario.get("papel") == "admin":
            admin = usuario
        else:
            membros.append(usuario)

    membros = sorted(membros, key=lambda item: item.get("nome", "").lower())

    return admin, membros


def pode_editar_usuario(usuario_logado, uid_alvo):
    """
    Admin pode editar todos da própria conta.
    Membro só pode editar ele mesmo.
    """

    if usuario_logado.get("papel") == "admin":
        return True

    return usuario_logado.get("uid") == uid_alvo


def pode_deletar_usuario(usuario_logado, uid_alvo):
    """
    Apenas admin pode deletar membros.
    Admin não pode deletar a si mesmo por esta tela.
    """

    if usuario_logado.get("papel") != "admin":
        return False

    if usuario_logado.get("uid") == uid_alvo:
        return False

    return True


def criar_usuario_membro(usuario_logado, nome, email, senha):
    """
    Cria um novo usuário no Firebase Auth e no Firestore.

    Apenas admin deve chamar esta função.
    """

    if usuario_logado.get("papel") != "admin":
        raise PermissionError("Apenas o administrador pode adicionar usuários.")

    admin_uid = obter_admin_uid(usuario_logado)

    usuario_auth = auth.create_user(
        email=email,
        password=senha,
        display_name=nome
    )

    dados_usuario = {
        "uid": usuario_auth.uid,
        "nome": nome,
        "email": email,
        "foto": None,
        "papel": "membro",
        "admin_uid": admin_uid,
        "ativo": True,
        "criado_em": firestore.SERVER_TIMESTAMP,
        "atualizado_em": firestore.SERVER_TIMESTAMP
    }

    db.collection("usuarios").document(usuario_auth.uid).set(dados_usuario)

    return dados_usuario


def atualizar_usuario(usuario_logado, uid_alvo, nome, email, senha=None):
    """
    Atualiza nome, e-mail e, opcionalmente, senha.

    A senha só é atualizada se vier preenchida.
    """

    if not pode_editar_usuario(usuario_logado, uid_alvo):
        raise PermissionError("Você não tem permissão para editar este usuário.")

    usuario_alvo = buscar_usuario_por_uid(uid_alvo)

    if not usuario_alvo:
        raise ValueError("Usuário não encontrado.")

    admin_uid_logado = obter_admin_uid(usuario_logado)

    if usuario_alvo.get("admin_uid") != admin_uid_logado:
        raise PermissionError("Usuário não pertence à sua conta.")

    dados_auth = {
        "display_name": nome,
        "email": email
    }

    if senha:
        dados_auth["password"] = senha

    auth.update_user(uid_alvo, **dados_auth)

    db.collection("usuarios").document(uid_alvo).update({
        "nome": nome,
        "email": email,
        "atualizado_em": firestore.SERVER_TIMESTAMP
    })

    usuario_atualizado = buscar_usuario_por_uid(uid_alvo)

    return usuario_atualizado


def deletar_usuario(usuario_logado, uid_alvo):
    """
    Deleta/desativa um usuário.

    Para evitar perder histórico, fazemos soft delete no Firestore.
    No Firebase Auth, o usuário é removido.
    """

    if not pode_deletar_usuario(usuario_logado, uid_alvo):
        raise PermissionError("Você não tem permissão para deletar este usuário.")

    usuario_alvo = buscar_usuario_por_uid(uid_alvo)

    if not usuario_alvo:
        raise ValueError("Usuário não encontrado.")

    admin_uid_logado = obter_admin_uid(usuario_logado)

    if usuario_alvo.get("admin_uid") != admin_uid_logado:
        raise PermissionError("Usuário não pertence à sua conta.")

    auth.delete_user(uid_alvo)

    db.collection("usuarios").document(uid_alvo).update({
        "ativo": False,
        "deletado_em": firestore.SERVER_TIMESTAMP
    })