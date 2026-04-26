# services/export_service.py

import json
from datetime import datetime, date
from decimal import Decimal

from config.firebase_config import iniciar_firebase


db = iniciar_firebase()


def _obter_admin_uid(usuario_logado):
    """
    Retorna o admin_uid do grupo.
    Se for admin, admin_uid será o próprio uid.
    """

    return usuario_logado.get("admin_uid") or usuario_logado.get("uid")


def _converter_valor_json(valor):
    """
    Converte valores que o JSON puro não entende,
    como datetime, date e Decimal.
    """

    if isinstance(valor, datetime):
        return valor.isoformat()

    if isinstance(valor, date):
        return valor.isoformat()

    if isinstance(valor, Decimal):
        return float(valor)

    return str(valor)


def _limpar_usuario_para_exportacao(usuario):
    """
    Remove ou evita campos sensíveis demais.

    Não exportamos senha, porque senha não fica disponível
    no Firebase Authentication e não deve ser exportada.
    """

    return {
        "uid": usuario.get("uid"),
        "nome": usuario.get("nome"),
        "email": usuario.get("email"),
        "papel": usuario.get("papel"),
        "admin_uid": usuario.get("admin_uid"),
        "ativo": usuario.get("ativo"),
        "foto": usuario.get("foto"),
        "acessibilidade": usuario.get("acessibilidade", {}),
        "criado_em": usuario.get("criado_em"),
        "atualizado_em": usuario.get("atualizado_em"),
        "deletado_em": usuario.get("deletado_em")
    }


def listar_usuarios_exportacao(admin_uid):
    """
    Lista os usuários vinculados ao mesmo admin_uid.
    """

    docs = (
        db.collection("usuarios")
        .where("admin_uid", "==", admin_uid)
        .stream()
    )

    usuarios = []

    for doc in docs:
        usuario = doc.to_dict()
        usuarios.append(_limpar_usuario_para_exportacao(usuario))

    return usuarios


def listar_alimentos_exportacao(admin_uid):
    """
    Lista todos os alimentos cadastrados no grupo.
    """

    docs = (
        db.collection("contas")
        .document(admin_uid)
        .collection("alimentos")
        .stream()
    )

    alimentos = []

    for doc in docs:
        alimento = doc.to_dict()
        alimentos.append(alimento)

    return alimentos


def montar_dados_exportacao(usuario_logado):
    """
    Monta o pacote completo de dados da aplicação
    para o grupo do usuário logado.
    """

    admin_uid = _obter_admin_uid(usuario_logado)

    dados_exportacao = {
        "metadata": {
            "aplicacao": "TechChef Dispensa",
            "formato": "json",
            "versao_exportacao": "1.0",
            "gerado_em": datetime.now().isoformat(),
            "gerado_por": {
                "uid": usuario_logado.get("uid"),
                "nome": usuario_logado.get("nome"),
                "email": usuario_logado.get("email"),
                "papel": usuario_logado.get("papel")
            },
            "admin_uid": admin_uid
        },
        "usuarios": listar_usuarios_exportacao(admin_uid),
        "alimentos": listar_alimentos_exportacao(admin_uid)
    }

    return dados_exportacao


def gerar_json_exportacao(usuario_logado):
    """
    Gera uma string JSON formatada para exportação.
    """

    dados = montar_dados_exportacao(usuario_logado)

    return json.dumps(
        dados,
        ensure_ascii=False,
        indent=4,
        default=_converter_valor_json
    )