from flask import Flask
from home.routes import home_bp


def create_app():
    flask_app = Flask(__name__)

    flask_app.register_blueprint(home_bp)

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
