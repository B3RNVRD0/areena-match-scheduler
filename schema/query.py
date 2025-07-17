import graphene
from schema.types import MatchType, TeamType 
from models.team import Team
from models.match import Match
from datetime import datetime 

class Query(graphene.ObjectType):


    all_matches = graphene.List(MatchType)
    def resolve_all_matches(self, info):
        return Match.query.all()

    match_by_id = graphene.Field(MatchType, id=graphene.Int(required=True))
    def resolve_match_by_id(self, info, id):
        return Match.query.get(id) 

    team_by_name = graphene.Field(TeamType, name=graphene.String(required=True))
    def resolve_team_by_name(self, info, name):
        return Team.query.filter_by(name=name).first()

    all_teams = graphene.List(TeamType)
    def resolve_all_teams(self, info):
        return Team.query.all()
