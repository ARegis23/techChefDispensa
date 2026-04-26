# services/auth_service.py

from firebase_admin import auth

from config.firebase_config import iniciar_firebase


iniciar_firebase()


def verificar_token_firebase(id_token):
    """
    Verifica o ID Token enviado pelo front-end.

    Se o token for válido, retorna os dados do usuário.
    Se for inválido, o Firebase Admin SDK lança erro.
    """

    decoded_token = auth.verify_id_token(id_token)

    usuario = {
        "uid": decoded_token.get("uid"),
        "nome": decoded_token.get("name", "Usuário"),
        "email": decoded_token.get("email"),
        "foto": decoded_token.get("picture")
    }

    return usuario