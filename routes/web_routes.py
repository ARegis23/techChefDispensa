# routes/web_routes.py

from flask import Blueprint, render_template, jsonify
from services.firestore_service import testar_conexao_firebase


web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template("index.html")


@web_bp.route("/teste-firebase")
def teste_firebase():
    resultado = testar_conexao_firebase()

    if resultado:
        return jsonify({
            "ok": True,
            "dados": resultado
        })

    return jsonify({
        "ok": False,
        "erro": "Não foi possível ler o documento no Firestore."
    }), 500