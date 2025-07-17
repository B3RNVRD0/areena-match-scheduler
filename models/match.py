from models import db
from datetime import datetime
from sqlalchemy.orm import relationship 

class Match(db.Model):
    __tablename__ = 'matches' 

    id = db.Column(db.Integer, primary_key=True)

    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    home_team_obj = relationship('Team', foreign_keys=[home_team_id], backref='home_matches', lazy='joined')
    away_team_obj = relationship('Team', foreign_keys=[away_team_id], backref='away_matches', lazy='joined')

    def __repr__(self):
        home_name = self.home_team_obj.name if self.home_team_obj else "N/A"
        away_name = self.away_team_obj.name if self.away_team_obj else "N/A"
        return f'<Match (ID: {self.id}) Home: {home_name} vs Away: {away_name} ({self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")})>'