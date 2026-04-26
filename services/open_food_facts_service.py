# services/open_food_facts_service.py

import requests


OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}"


def _pegar_valor_nutriente(nutriments, chave, padrao=""):
    """
    Busca um nutriente no retorno da API.

    A Open Food Facts normalmente retorna valores por 100g,
    por exemplo: carbohydrates_100g, proteins_100g, fat_100g.
    """

    valor = nutriments.get(chave)

    if valor is None:
        return padrao

    return valor


def buscar_alimento_por_barcode_api(barcode):
    """
    Busca um produto na Open Food Facts usando o código de barras.

    Retorna um dicionário padronizado para o nosso sistema.
    Se não encontrar, retorna None.
    """

    if not barcode:
        return None

    url = OPEN_FOOD_FACTS_URL.format(barcode=barcode)

    params = {
        "fields": ",".join([
            "code",
            "product_name",
            "brands",
            "quantity",
            "categories",
            "allergens",
            "allergens_tags",
            "nutriments"
        ])
    }

    headers = {
        "User-Agent": "TechChefDispensa/1.0 - Projeto Academico"
    }

    try:
        resposta = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        if resposta.status_code != 200:
            return None

        dados = resposta.json()

        if dados.get("status") != 1:
            return None

        produto = dados.get("product", {})
        nutriments = produto.get("nutriments", {})

        # Na Open Food Facts, sodium_100g costuma vir em gramas por 100g.
        # Para facilitar leitura nutricional, armazenamos sódio em mg/100g.
        sodio_g = _pegar_valor_nutriente(nutriments, "sodium_100g", "")
        sodio_mg = ""

        if sodio_g != "":
            try:
                sodio_mg = float(sodio_g) * 1000
            except ValueError:
                sodio_mg = ""

        alimento = {
            "barcode": barcode,
            "nome": produto.get("product_name", ""),
            "marca": produto.get("brands", ""),
            "peso": produto.get("quantity", ""),
            "categoria": produto.get("categories", ""),
            "alergenos": produto.get("allergens", ""),

            "kcal": _pegar_valor_nutriente(nutriments, "energy-kcal_100g", ""),
            "carboidratos": _pegar_valor_nutriente(nutriments, "carbohydrates_100g", ""),
            "proteinas": _pegar_valor_nutriente(nutriments, "proteins_100g", ""),
            "fibras": _pegar_valor_nutriente(nutriments, "fiber_100g", ""),
            "sodio": sodio_mg,
            "gorduras_totais": _pegar_valor_nutriente(nutriments, "fat_100g", ""),
            "gorduras_saturadas": _pegar_valor_nutriente(nutriments, "saturated-fat_100g", ""),
            "gorduras_trans": _pegar_valor_nutriente(nutriments, "trans-fat_100g", ""),
            "acucares_totais": _pegar_valor_nutriente(nutriments, "sugars_100g", ""),
            "acucares_adicionados": _pegar_valor_nutriente(nutriments, "added-sugars_100g", ""),

            "origem_dados": "api"
        }

        return alimento

    except requests.RequestException as erro:
        print("Erro ao consultar Open Food Facts:", erro)
        return None