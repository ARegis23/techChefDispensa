# services/open_food_facts_service.py

import requests


def buscar_alimento_por_barcode_api(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}"

    headers = {
        "User-Agent": "TechChefDespensa/1.0 - Projeto Academico"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        data = response.json()

        if data.get("status") != 1:
            return None

        produto = data.get("product", {})

        return {
            "barcode": barcode,
            "nome": produto.get("product_name"),
            "marca": produto.get("brands"),
            "categoria": produto.get("categories"),

            "peso": produto.get("quantity"),
            "alergenos": produto.get("allergens"),

            "kcal": _get_nested(produto, ["nutriments", "energy-kcal"]),
            "carboidratos": _get_nested(produto, ["nutriments", "carbohydrates"]),
            "proteinas": _get_nested(produto, ["nutriments", "proteins"]),
            "fibras": _get_nested(produto, ["nutriments", "fiber"]),
            "sodio": _get_nested(produto, ["nutriments", "sodium"]),

            "gorduras_totais": _get_nested(produto, ["nutriments", "fat"]),
            "gorduras_saturadas": _get_nested(produto, ["nutriments", "saturated-fat"]),
            "gorduras_trans": _get_nested(produto, ["nutriments", "trans-fat"]),

            "acucares_totais": _get_nested(produto, ["nutriments", "sugars"]),
            "acucares_adicionados": None,

            "origem_dados": "api"
        }

    except Exception as e:
        print("Erro na API Open Food Facts:", e)
        return None


def _get_nested(d, keys):
    """
    Acessa dicionario aninhado com seguranca.
    """
    for key in keys:
        if not d or key not in d:
            return None
        d = d[key]
    return d
