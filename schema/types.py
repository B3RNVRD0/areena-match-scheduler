import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models.team import Team 
from models.match import Match 

class TeamType(SQLAlchemyObjectType):
    class Meta:
        model = Team 

class MatchType(SQLAlchemyObjectType):
    class Meta:
        model = Match 

    home_team = graphene.Field(TeamType)
    away_team = graphene.Field(TeamType)

    # Resolvers 
    # defined in model Match.
    def resolve_home_team(parent, info):
        return parent.home_team_obj

    def resolve_away_team(parent, info):
        return parent.away_team_obj