# services/importacao_service.py

from google.cloud import firestore

from config.firebase_config import iniciar_firebase
from services.open_food_facts_service import buscar_alimento_por_barcode_api


db = iniciar_firebase()


def _obter_admin_uid(usuario_logado):
    """
    Retorna o identificador do grupo/conta principal.
    """

    return usuario_logado.get("admin_uid") or usuario_logado.get("uid")


def _referencia_importacoes(usuario_logado):
    """
    Retorna a coleção de importações do grupo.
    """

    admin_uid = _obter_admin_uid(usuario_logado)

    return (
        db.collection("contas")
        .document(admin_uid)
        .collection("importacoes")
    )


def _converter_para_float(valor):
    """
    Converte valor numérico para float.
    """

    if valor is None or valor == "":
        return None

    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def listar_importacoes(usuario_logado):
    """
    Lista todas as importações do grupo.
    """

    docs = (
        _referencia_importacoes(usuario_logado)
        .order_by("criado_em", direction=firestore.Query.DESCENDING)
        .stream()
    )

    importacoes = []

    for doc in docs:
        dados = doc.to_dict()
        dados["id"] = doc.id
        importacoes.append(dados)

    return importacoes


def buscar_importacao(usuario_logado, importacao_id):
    """
    Busca uma importação específica.
    """

    doc = (
        _referencia_importacoes(usuario_logado)
        .document(importacao_id)
        .get()
    )

    if doc.exists:
        dados = doc.to_dict()
        dados["id"] = doc.id
        return dados

    return None


def importar_por_barcode(usuario_logado, barcode):
    """
    Busca dados em API externa por barcode e salva na coleção importacoes.
    """

    if not barcode:
        raise ValueError("O código de barras é obrigatório.")

    barcode = barcode.strip()

    dados_api = buscar_alimento_por_barcode_api(barcode)

    if dados_api:
        status = "importado"
        observacao = "Dados importados da API Open Food Facts."
    else:
        status = "nao_encontrado"
        observacao = "Produto não encontrado na API. Registro criado para revisão manual."
        dados_api = {
            "barcode": barcode,
            "nome": "",
            "marca": "",
            "categoria": "",
            "peso": "",
            "alergenos": "",
            "kcal": None,
            "carboidratos": None,
            "proteinas": None,
            "fibras": None,
            "sodio": None,
            "gorduras_totais": None,
            "gorduras_saturadas": None,
            "gorduras_trans": None,
            "acucares_totais": None,
            "acucares_adicionados": None,
            "origem_dados": "manual"
        }

    admin_uid = _obter_admin_uid(usuario_logado)

    dados_importacao = {
        "barcode": barcode,

        "nome": dados_api.get("nome"),
        "marca": dados_api.get("marca"),
        "categoria": dados_api.get("categoria"),
        "peso": dados_api.get("peso"),
        "alergenos": dados_api.get("alergenos"),

        "kcal": _converter_para_float(dados_api.get("kcal")),
        "carboidratos": _converter_para_float(dados_api.get("carboidratos")),
        "proteinas": _converter_para_float(dados_api.get("proteinas")),
        "fibras": _converter_para_float(dados_api.get("fibras")),
        "sodio": _converter_para_float(dados_api.get("sodio")),
        "gorduras_totais": _converter_para_float(dados_api.get("gorduras_totais")),
        "gorduras_saturadas": _converter_para_float(dados_api.get("gorduras_saturadas")),
        "gorduras_trans": _converter_para_float(dados_api.get("gorduras_trans")),
        "acucares_totais": _converter_para_float(dados_api.get("acucares_totais")),
        "acucares_adicionados": _converter_para_float(dados_api.get("acucares_adicionados")),

        "origem": "Open Food Facts",
        "origem_dados": dados_api.get("origem_dados", "api"),
        "url_consulta": f"https://world.openfoodfacts.org/api/v2/product/{barcode}",

        "status": status,
        "observacao": observacao,

        "admin_uid": admin_uid,
        "importado_por": usuario_logado.get("uid"),
        "importado_por_nome": usuario_logado.get("nome"),

        "criado_em": firestore.SERVER_TIMESTAMP,
        "atualizado_em": firestore.SERVER_TIMESTAMP
    }

    doc_ref = _referencia_importacoes(usuario_logado).document()
    doc_ref.set(dados_importacao)

    dados_importacao["id"] = doc_ref.id

    return dados_importacao


def montar_dados_importacao_formulario(formulario, usuario_logado):
    """
    Monta os dados editáveis da importação a partir do formulário.
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

        "status": formulario.get("status", "revisado"),
        "observacao": formulario.get("observacao", "").strip(),

        "admin_uid": admin_uid,
        "atualizado_por": usuario_logado.get("uid"),
        "atualizado_por_nome": usuario_logado.get("nome"),
        "atualizado_em": firestore.SERVER_TIMESTAMP
    }


def atualizar_importacao(usuario_logado, importacao_id, dados_importacao):
    """
    Atualiza uma importação existente.
    """

    existente = buscar_importacao(usuario_logado, importacao_id)

    if not existente:
        raise ValueError("Importação não encontrada.")

    _referencia_importacoes(usuario_logado).document(importacao_id).update(dados_importacao)

    return buscar_importacao(usuario_logado, importacao_id)


def deletar_importacao(usuario_logado, importacao_id):
    """
    Deleta uma importação.
    """

    existente = buscar_importacao(usuario_logado, importacao_id)

    if not existente:
        raise ValueError("Importação não encontrada.")

    _referencia_importacoes(usuario_logado).document(importacao_id).delete()


def marcar_importacao_enviada_para_alimentos(usuario_logado, importacao_id):
    """
    Marca uma importação como enviada para alimentos.
    """

    _referencia_importacoes(usuario_logado).document(importacao_id).update({
        "status": "enviado_para_alimentos",
        "atualizado_por": usuario_logado.get("uid"),
        "atualizado_por_nome": usuario_logado.get("nome"),
        "atualizado_em": firestore.SERVER_TIMESTAMP
    })