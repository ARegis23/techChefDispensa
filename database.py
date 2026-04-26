import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()


def inicializar_firebase():
    """
    Inicializa a conexão com o Firebase apenas uma vez.
    """

    if firebase_admin._apps:
        return firestore.client()

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if cred_path:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

    return firestore.client()


db = inicializar_firebase()


def buscar_usuario_por_username(username):
    """
    Busca um usuário pelo nome de usuário.
    Retorna um dicionário com os dados ou None.
    """

    usuarios_ref = db.collection("usuarios")
    consulta = usuarios_ref.where("username", "==", username).limit(1).stream()

    for doc in consulta:
        usuario = doc.to_dict()
        usuario["id"] = doc.id
        return usuario

    return None


def criar_usuario_inicial():
    """
    Cria um usuário admin inicial caso ele ainda não exista.
    Isso ajuda a conseguir fazer o primeiro login no sistema.
    """

    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    usuario_existente = buscar_usuario_por_username(admin_user)

    if usuario_existente:
        return

    novo_usuario = {
        "nome": "Administrador",
        "username": admin_user,
        "senha_hash": generate_password_hash(admin_password),
        "perfil": "admin",
        "ativo": True
    }

    db.collection("usuarios").add(novo_usuario)


def listar_documentos(nome_colecao):
    """
    Lista todos os documentos de uma coleção.
    """

    documentos = db.collection(nome_colecao).stream()
    lista = []

    for doc in documentos:
        item = doc.to_dict()
        item["id"] = doc.id
        lista.append(item)

    return lista


def buscar_documento_por_id(nome_colecao, documento_id):
    """
    Busca um documento específico pelo ID.
    """

    doc = db.collection(nome_colecao).document(documento_id).get()

    if doc.exists:
        item = doc.to_dict()
        item["id"] = doc.id
        return item

    return None


def adicionar_documento(nome_colecao, dados):
    """
    Adiciona um documento em uma coleção.
    """

    return db.collection(nome_colecao).add(dados)


def atualizar_documento(nome_colecao, documento_id, dados):
    """
    Atualiza um documento existente.
    """

    db.collection(nome_colecao).document(documento_id).update(dados)


def deletar_documento(nome_colecao, documento_id):
    """
    Remove um documento da coleção.
    """

    db.collection(nome_colecao).document(documento_id).delete()