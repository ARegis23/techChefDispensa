# services/alimento_service.py

from google.cloud import firestore

from config.firebase_config import iniciar_firebase


db = iniciar_firebase()


def validar_float(valor, campo_nome):
    """
    Converte valores numericos vindos do formulario.
    Se vier vazio, retorna None. Se vier invalido, avisa o campo.
    """

    if valor is None or valor == "":
        return None

    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        raise ValueError(f"O campo '{campo_nome}' deve ser numérico.")


def _validar_barcode(barcode):
    if not barcode or len(barcode) < 8:
        raise ValueError("Barcode inválido.")

    if not barcode.isdigit():
        raise ValueError("Barcode deve conter apenas números.")


def _normalizar_dados_alimento(dados_alimento):
    campos_texto_titulo = ["nome", "marca", "categoria"]
    campos_texto = ["peso", "alergenos"]
    campos_numericos = {
        "kcal": "Kcal",
        "carboidratos": "Carboidratos",
        "proteinas": "Proteínas",
        "fibras": "Fibras",
        "sodio": "Sódio",
        "gorduras_totais": "Gorduras totais",
        "gorduras_saturadas": "Gorduras saturadas",
        "gorduras_trans": "Gorduras trans",
        "acucares_totais": "Açúcares totais",
        "acucares_adicionados": "Açúcares adicionados",
    }

    for campo in campos_texto_titulo:
        if dados_alimento.get(campo) is not None:
            dados_alimento[campo] = str(dados_alimento.get(campo, "")).strip().title()

    for campo in campos_texto:
        if dados_alimento.get(campo) is not None:
            dados_alimento[campo] = str(dados_alimento.get(campo, "")).strip()

    for campo, nome in campos_numericos.items():
        dados_alimento[campo] = validar_float(dados_alimento.get(campo), nome)

    return dados_alimento


def _obter_admin_uid(usuario_logado):
    """
    Retorna o admin_uid que identifica o grupo/conta principal.
    """

    return usuario_logado.get("admin_uid") or usuario_logado.get("uid")


def _referencia_alimentos(usuario_logado):
    """
    Retorna a colecao compartilhada de alimentos do grupo.
    """

    admin_uid = _obter_admin_uid(usuario_logado)

    return (
        db.collection("contas")
        .document(admin_uid)
        .collection("alimentos")
    )


def montar_dados_alimento(formulario, usuario_logado):
    """
    Monta o dicionario do alimento a partir do formulario HTML.
    """

    admin_uid = _obter_admin_uid(usuario_logado)

    return {
        "barcode": formulario.get("barcode", "").strip(),
        "nome": formulario.get("nome", "").strip().title(),
        "marca": formulario.get("marca", "").strip().title(),
        "categoria": formulario.get("categoria", "").strip().title(),
        "peso": formulario.get("peso", "").strip(),
        "alergenos": formulario.get("alergenos", "").strip(),

        "kcal": validar_float(formulario.get("kcal"), "Kcal"),
        "carboidratos": validar_float(formulario.get("carboidratos"), "Carboidratos"),
        "proteinas": validar_float(formulario.get("proteinas"), "Proteínas"),
        "fibras": validar_float(formulario.get("fibras"), "Fibras"),
        "sodio": validar_float(formulario.get("sodio"), "Sódio"),
        "gorduras_totais": validar_float(formulario.get("gorduras_totais"), "Gorduras totais"),
        "gorduras_saturadas": validar_float(formulario.get("gorduras_saturadas"), "Gorduras saturadas"),
        "gorduras_trans": validar_float(formulario.get("gorduras_trans"), "Gorduras trans"),
        "acucares_totais": validar_float(formulario.get("acucares_totais"), "Açúcares totais"),
        "acucares_adicionados": validar_float(formulario.get("acucares_adicionados"), "Açúcares adicionados"),

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

    barcode = str(dados_alimento.get("barcode", "")).strip()
    dados_alimento["barcode"] = barcode

    _validar_barcode(barcode)
    dados_alimento = _normalizar_dados_alimento(dados_alimento)

    if not dados_alimento.get("nome"):
        raise ValueError("O nome do alimento é obrigatório.")

    existente = buscar_alimento(usuario_logado, barcode)

    if existente:
        raise ValueError("Esse produto já está cadastrado.")

    dados_alimento["criado_por"] = usuario_logado.get("uid")
    dados_alimento["criado_por_nome"] = usuario_logado.get("nome")
    dados_alimento["criado_em"] = firestore.SERVER_TIMESTAMP

    _referencia_alimentos(usuario_logado).document(barcode).set(dados_alimento)

    return dados_alimento


def atualizar_alimento(usuario_logado, barcode, dados_alimento):
    """
    Atualiza um alimento compartilhado do grupo.
    """

    barcode = str(barcode).strip()
    _validar_barcode(barcode)
    dados_alimento = _normalizar_dados_alimento(dados_alimento)

    if not dados_alimento.get("nome"):
        raise ValueError("O nome do alimento é obrigatório.")

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
