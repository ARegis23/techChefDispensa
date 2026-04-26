# services/alimento_service.py

from google.cloud import firestore

from config.firebase_config import iniciar_firebase


db = iniciar_firebase()


def _converter_para_float(valor):
    """
    Converte valores numéricos vindos do formulário.
    Se vier vazio, retorna None.
    """

    if valor is None or valor == "":
        return None

    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def _obter_admin_uid(usuario_logado):
    """
    Retorna o admin_uid que identifica o grupo/conta principal.

    Admin:
        uid == admin_uid

    Membro:
        admin_uid aponta para o admin principal
    """

    admin_uid = usuario_logado.get("admin_uid")

    if not admin_uid:
        admin_uid = usuario_logado.get("uid")

    return admin_uid


def _referencia_alimentos(usuario_logado):
    """
    Retorna a coleção compartilhada de alimentos do grupo.

    Todos os usuários do mesmo admin_uid acessam
    a mesma coleção de alimentos.
    """

    admin_uid = _obter_admin_uid(usuario_logado)

    return (
        db.collection("contas")
        .document(admin_uid)
        .collection("alimentos")
    )


def montar_dados_alimento(formulario, usuario_logado):
    """
    Monta o dicionário do alimento a partir do formulário HTML.
    """

    admin_uid = _obter_admin_uid(usuario_logado)

    return {
        "barcode": formulario.get("barcode", "").strip(),
        "nome": formulario.get("nome", "").strip(),
        "marca": formulario.get("marca", "").strip(),
        "categoria": formulario.get("categoria", "").strip(),
        "peso": formulario.get("peso", "").strip(),
        "alergenos": formulario.get("alergenos", "").strip(),

        "kcal": _converter_para_float(formulario.get("kcal")),
        "carboidratos": _converter_para_float(formulario.get("carboidratos")),
        "proteinas": _converter_para_float(formulario.get("proteinas")),
        "fibras": _converter_para_float(formulario.get("fibras")),
        "sodio": _converter_para_float(formulario.get("sodio")),
        "gorduras_totais": _converter_para_float(formulario.get("gorduras_totais")),
        "gorduras_saturadas": _converter_para_float(formulario.get("gorduras_saturadas")),
        "gorduras_trans": _converter_para_float(formulario.get("gorduras_trans")),
        "acucares_totais": _converter_para_float(formulario.get("acucares_totais")),
        "acucares_adicionados": _converter_para_float(formulario.get("acucares_adicionados")),

        "origem_dados": formulario.get("origem_dados", "manual"),
        "admin_uid": admin_uid,

        "atualizado_por": usuario_logado.get("uid"),
        "atualizado_por_nome": usuario_logado.get("nome"),
        "atualizado_em": firestore.SERVER_TIMESTAMP
    }


def listar_alimentos(usuario_logado):
    """
    Lista todos os alimentos compartilhados do grupo.
    """

    docs = (
        _referencia_alimentos(usuario_logado)
        .order_by("nome")
        .stream()
    )

    alimentos = []

    for doc in docs:
        alimento = doc.to_dict()
        alimentos.append(alimento)

    return alimentos


def buscar_alimento(usuario_logado, barcode):
    """
    Busca um alimento pelo barcode dentro do grupo.
    """

    doc = (
        _referencia_alimentos(usuario_logado)
        .document(barcode)
        .get()
    )

    if doc.exists:
        return doc.to_dict()

    return None


def criar_alimento(usuario_logado, dados_alimento):
    """
    Cria um alimento compartilhado no grupo usando o barcode como ID.
    """

    barcode = dados_alimento.get("barcode")

    if not barcode:
        raise ValueError("O código de barras é obrigatório.")

    existente = buscar_alimento(usuario_logado, barcode)

    if existente:
        raise ValueError("Já existe um alimento cadastrado com este código de barras.")

    dados_alimento["criado_por"] = usuario_logado.get("uid")
    dados_alimento["criado_por_nome"] = usuario_logado.get("nome")
    dados_alimento["criado_em"] = firestore.SERVER_TIMESTAMP

    _referencia_alimentos(usuario_logado).document(barcode).set(dados_alimento)

    return dados_alimento


def atualizar_alimento(usuario_logado, barcode, dados_alimento):
    """
    Atualiza um alimento compartilhado do grupo.
    """

    existente = buscar_alimento(usuario_logado, barcode)

    if not existente:
        raise ValueError("Alimento não encontrado.")

    dados_alimento["barcode"] = barcode
    dados_alimento["atualizado_por"] = usuario_logado.get("uid")
    dados_alimento["atualizado_por_nome"] = usuario_logado.get("nome")
    dados_alimento["atualizado_em"] = firestore.SERVER_TIMESTAMP

    _referencia_alimentos(usuario_logado).document(barcode).update(dados_alimento)

    return buscar_alimento(usuario_logado, barcode)


def deletar_alimento(usuario_logado, barcode):
    """
    Deleta um alimento compartilhado do grupo.
    """

    existente = buscar_alimento(usuario_logado, barcode)

    if not existente:
        raise ValueError("Alimento não encontrado.")

    _referencia_alimentos(usuario_logado).document(barcode).delete()