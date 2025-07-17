# app.py
import os
from flask import Flask, jsonify
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        if not os.path.exists('instance'):
            os.makedirs('instance')

    db.init_app(app)

    from models.team import Team
    from models.match import Match

    @app.route('/')
    def index():
        return "API is running! Visit /init-db to set up the database."

    @app.route('/init-db')
    def init_db_endpoint():
        with app.app_context():
            db.create_all() 

            #  test
            if not Team.query.first(): 
                team_alpha = Team(name='Team Alpha')
                team_beta = Team(name='Team Beta')
                team_gamma = Team(name='Team Gamma')
                team_delta = Team(name='Team Delta') 
                db.session.add_all([team_alpha, team_beta, team_gamma, team_delta])
                db.session.commit()
                return jsonify({"message": "Database initialized and test teams added!"}), 200
            else:
                return jsonify({"message": "Database already initialized and teams might exist."}), 200


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)