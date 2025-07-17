# app.py
import os
from flask import Flask, jsonify
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # tests
    if app.config.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else: 
        if not os.path.exists('instance'):
            os.makedirs('instance')

    db.init_app(app)

    # AQUI FICARÃO AS IMPORTAÇÕES DOS SEUS MODELOS (Team, Match) NO PRÓXIMO PASSO
    # from models.team import Team
    # from models.match import Match

    @app.route('/')
    def index():
        return "API is running! Visit /init-db to set up the database."

    @app.route('/init-db')
    def init_db_endpoint():
        with app.app_context():
            db.create_all() 
            return jsonify({"message": "Database initialized (tables created, no teams yet)!"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)