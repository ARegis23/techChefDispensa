from google.cloud import firestore

from config.firebase_config import iniciar_firebase
from services.open_food_facts_service import buscar_alimento_por_barcode_api

db = iniciar_firebase()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _obter_admin_uid(usuario_logado):
    return usuario_logado.get("admin_uid") or usuario_logado.get("uid")


def _referencia_importacoes(usuario_logado):
    admin_uid = _obter_admin_uid(usuario_logado)

    return (
        db.collection("contas")
        .document(admin_uid)
        .collection("importacoes")
    )


def _converter_para_float(valor):
    if valor is None or valor == "":
        return None

    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


# ─────────────────────────────────────────────
# CRIAR VIA API
# ─────────────────────────────────────────────

def importar_por_barcode(usuario_logado, barcode):
    if not barcode:
        raise ValueError("O código de barras é obrigatório.")

    barcode = barcode.strip()
    dados_api = buscar_alimento_por_barcode_api(barcode)

    if dados_api:
        status = "importado"
        observacao = "Dados importados da API."
    else:
        status = "nao_encontrado"
        observacao = "Produto não encontrado. Preencher manualmente."
        dados_api = {"barcode": barcode}

    dados = {
        "barcode": barcode,
        "nome": dados_api.get("nome", ""),
        "marca": dados_api.get("marca", ""),
        "categoria": dados_api.get("categoria", ""),
        "peso": dados_api.get("peso", ""),
        "alergenos": dados_api.get("alergenos", ""),

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

        "origem": dados_api.get("origem_dados", "manual"),
        "origem_dados": dados_api.get("origem_dados", "manual"),
        "status": status,
        "observacao": observacao,

        "admin_uid": _obter_admin_uid(usuario_logado),
        "criado_por": usuario_logado.get("uid"),
        "criado_por_nome": usuario_logado.get("nome"),
        "importado_por": usuario_logado.get("uid"),
        "importado_por_nome": usuario_logado.get("nome"),

        "criado_em": firestore.SERVER_TIMESTAMP,
        "atualizado_em": firestore.SERVER_TIMESTAMP,
    }

    ref = _referencia_importacoes(usuario_logado).document()
    ref.set(dados)

    dados["id"] = ref.id
    return dados


# ─────────────────────────────────────────────
# CRIAR MANUAL (🔥 NOVO - resolve seu erro)
# ─────────────────────────────────────────────

def criar_importacao(usuario_logado, dados):
    ref = _referencia_importacoes(usuario_logado).document()

    dados_final = {
        **dados,
        "admin_uid": _obter_admin_uid(usuario_logado),
        "criado_por": usuario_logado.get("uid"),
        "criado_por_nome": usuario_logado.get("nome"),
        "status": "pendente",
        "criado_em": firestore.SERVER_TIMESTAMP,
        "atualizado_em": firestore.SERVER_TIMESTAMP,
    }

    ref.set(dados_final)
    dados_final["id"] = ref.id

    return dados_final


# ─────────────────────────────────────────────
# LISTAR
# ─────────────────────────────────────────────

def registrar_importacao_arquivo_json(usuario_logado, alimento, nome_arquivo=None):
    """
    Registra em importacoes um alimento recebido por arquivo JSON externo.
    """

    ref = _referencia_importacoes(usuario_logado).document()

    dados = {
        "barcode": alimento.get("barcode", ""),
        "nome": alimento.get("nome", ""),
        "marca": alimento.get("marca", ""),
        "categoria": alimento.get("categoria", ""),
        "peso": alimento.get("peso", ""),
        "alergenos": alimento.get("alergenos", ""),

        "kcal": _converter_para_float(alimento.get("kcal")),
        "carboidratos": _converter_para_float(alimento.get("carboidratos")),
        "proteinas": _converter_para_float(alimento.get("proteinas")),
        "fibras": _converter_para_float(alimento.get("fibras")),
        "sodio": _converter_para_float(alimento.get("sodio")),
        "gorduras_totais": _converter_para_float(alimento.get("gorduras_totais")),
        "gorduras_saturadas": _converter_para_float(alimento.get("gorduras_saturadas")),
        "gorduras_trans": _converter_para_float(alimento.get("gorduras_trans")),
        "acucares_totais": _converter_para_float(alimento.get("acucares_totais")),
        "acucares_adicionados": _converter_para_float(alimento.get("acucares_adicionados")),

        "origem": "Documento externo (JSON)",
        "origem_dados": "arquivo_json",
        "arquivo_origem": nome_arquivo or "",
        "status": "enviado_para_alimentos",
        "observacao": "Importado a partir de um documento JSON externo enviado pelo usuario.",

        "admin_uid": _obter_admin_uid(usuario_logado),
        "criado_por": usuario_logado.get("uid"),
        "criado_por_nome": usuario_logado.get("nome"),
        "importado_por": usuario_logado.get("uid"),
        "importado_por_nome": usuario_logado.get("nome"),

        "criado_em": firestore.SERVER_TIMESTAMP,
        "atualizado_em": firestore.SERVER_TIMESTAMP,
    }

    ref.set(dados)
    dados["id"] = ref.id

    return dados


def listar_importacoes(usuario_logado):
    docs = (
        _referencia_importacoes(usuario_logado)
        .order_by("criado_em", direction=firestore.Query.DESCENDING)
        .stream()
    )

    lista = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        lista.append(d)

    return lista


# ─────────────────────────────────────────────
# BUSCAR
# ─────────────────────────────────────────────

def buscar_importacao(usuario_logado, importacao_id):
    doc = _referencia_importacoes(usuario_logado).document(importacao_id).get()

    if doc.exists:
        dados = doc.to_dict()
        dados["id"] = doc.id
        return dados

    return None


# ─────────────────────────────────────────────
# MONTAR FORMULÁRIO (🔥 ESSENCIAL)
# ─────────────────────────────────────────────

def montar_dados_importacao_formulario(form, usuario_logado):
    return {
        "barcode": form.get("barcode"),
        "nome": form.get("nome"),
        "marca": form.get("marca"),
        "categoria": form.get("categoria"),
        "peso": form.get("peso"),
        "alergenos": form.get("alergenos"),

        "kcal": _converter_para_float(form.get("kcal")),
        "carboidratos": _converter_para_float(form.get("carboidratos")),
        "proteinas": _converter_para_float(form.get("proteinas")),
        "fibras": _converter_para_float(form.get("fibras")),
        "sodio": _converter_para_float(form.get("sodio")),
        "gorduras_totais": _converter_para_float(form.get("gorduras_totais")),
        "gorduras_saturadas": _converter_para_float(form.get("gorduras_saturadas")),
        "gorduras_trans": _converter_para_float(form.get("gorduras_trans")),
        "acucares_totais": _converter_para_float(form.get("acucares_totais")),
        "acucares_adicionados": _converter_para_float(form.get("acucares_adicionados")),

        "status": form.get("status", "revisado"),
        "observacao": form.get("observacao", ""),

        "atualizado_por": usuario_logado.get("uid"),
        "atualizado_por_nome": usuario_logado.get("nome"),
        "atualizado_em": firestore.SERVER_TIMESTAMP,
    }


# ─────────────────────────────────────────────
# ATUALIZAR
# ─────────────────────────────────────────────

def atualizar_importacao(usuario_logado, importacao_id, dados):
    _referencia_importacoes(usuario_logado).document(importacao_id).update(dados)


# ─────────────────────────────────────────────
# DELETAR
# ─────────────────────────────────────────────

def deletar_importacao(usuario_logado, importacao_id):
    _referencia_importacoes(usuario_logado).document(importacao_id).delete()


# ─────────────────────────────────────────────
# APROVAR
# ─────────────────────────────────────────────

def aprovar_importacao(usuario_logado, importacao_id):
    from services.alimento_service import criar_alimento

    imp = buscar_importacao(usuario_logado, importacao_id)

    if not imp:
        raise ValueError("Importação não encontrada.")

    criar_alimento(usuario_logado, imp)

    atualizar_importacao(usuario_logado, importacao_id, {
        "status": "aprovado"
    })


# ─────────────────────────────────────────────
# MARCAR ENVIADO
# ─────────────────────────────────────────────

def marcar_importacao_enviada_para_alimentos(usuario_logado, importacao_id):
    atualizar_importacao(usuario_logado, importacao_id, {
        "status": "enviado_para_alimentos"
    })
