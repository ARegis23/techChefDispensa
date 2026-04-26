# services/firestore_service.py

from config.firebase_config import iniciar_firebase


db = iniciar_firebase()


def testar_conexao_firebase():
    """
    Grava um documento simples no Firestore
    para verificar se a conexão está funcionando.
    """

    dados_teste = {
        "nome": "TechChef Dispensa",
        "status": "conexao_ok",
        "mensagem": "Firebase conectado com sucesso."
    }

    db.collection("testes").document("conexao").set(dados_teste)

    documento = db.collection("testes").document("conexao").get()

    if documento.exists:
        return documento.to_dict()

    return None