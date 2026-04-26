# config/firebase_config.py

import os
import firebase_admin
from firebase_admin import credentials, firestore


def iniciar_firebase():
    """
    Inicializa o Firebase Admin SDK.

    Essa função cria a conexão entre o Flask/Python e o Firebase.
    Ela usa a chave privada salva em secrets/serviceAccountKey.json.
    """

    caminho_credencial = os.getenv(
        "FIREBASE_CREDENTIALS",
        "secrets/serviceAccountKey.json"
    )

    if not firebase_admin._apps:
        cred = credentials.Certificate(caminho_credencial)
        firebase_admin.initialize_app(cred)

    return firestore.client()