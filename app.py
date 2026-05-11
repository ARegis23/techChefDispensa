import os

from flask import Flask
from dotenv import load_dotenv

from routes.web_routes import web_bp


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-techchef-despensa"
    )

    app.register_blueprint(web_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)