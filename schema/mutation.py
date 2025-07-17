import graphene
from models import db
from models.team import Team
from models.match import Match
from schema.types import MatchType, TeamType
from datetime import datetime


def check_team_availability(team_id, new_start, new_end, exclude_match_id=None):
    query = Match.query.filter(
        (
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        ) & (
            (Match.start_time < new_end) & (Match.end_time > new_start)
        )
    )
    if exclude_match_id:
        query = query.filter(Match.id != exclude_match_id)

    conflicting_matches = query.first()
    return conflicting_matches is not None


# CreateMatch 

class CreateMatchInput(graphene.InputObjectType):
    home_team_id = graphene.Int(required=True)
    away_team_id = graphene.Int(required=True)
    start_time = graphene.DateTime(required=True)
    end_time = graphene.DateTime(required=True)

class CreateMatch(graphene.Mutation):
    class Output(graphene.ObjectType):
        class Meta:
            name = "CreateMatchPayload"
        match = graphene.Field(MatchType)
        success = graphene.Boolean()
        message = graphene.String()

    class Arguments:
        input = CreateMatchInput(required=True)

    def mutate(self, info, input):
        home_team_id = input.home_team_id
        away_team_id = input.away_team_id
        start_time = input.start_time
        end_time = input.end_time

        if home_team_id == away_team_id:
            return CreateMatch.Output(success=False, message="Home team and away team cannot be the same.")

        if start_time >= end_time:
            return CreateMatch.Output(success=False, message="Start time must be before end time.")

        home_team = Team.query.get(home_team_id)
        away_team = Team.query.get(away_team_id)

        if not home_team or not away_team:
            return CreateMatch.Output(success=False, message="One or both teams not found.")

        if check_team_availability(home_team_id, start_time, end_time):
            return CreateMatch.Output(success=False, message=f"Home team '{home_team.name}' is already booked during this time slot.")

        if check_team_availability(away_team_id, start_time, end_time):
            return CreateMatch.Output(success=False, message=f"Away team '{away_team.name}' is already booked during this time slot.")

        new_match = Match(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(new_match)
        db.session.commit()

        return CreateMatch.Output(
            match=new_match,
            success=True,
            message="Match created successfully!"
        )

#  DeleteMatch 

class DeleteMatch(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    class Output(graphene.ObjectType):
        class Meta:
            name = "DeleteMatchPayload"
        success = graphene.Boolean()
        message = graphene.String()

    def mutate(self, info, id):
        match_to_delete = Match.query.get(id)

        if not match_to_delete:
            return DeleteMatch.Output(success=False, message=f"Match with ID {id} not found.")

        db.session.delete(match_to_delete)
        db.session.commit()

        return DeleteMatch.Output(success=True, message=f"Match with ID {id} deleted successfully.")


# SwapTeams
class SwapTeamsInput(graphene.InputObjectType):
    match_id = graphene.Int(required=True)
    new_home_team_id = graphene.Int(required=True)
    new_away_team_id = graphene.Int(required=True)

class SwapTeams(graphene.Mutation):
    class Arguments:
        input = SwapTeamsInput(required=True)

    class Output(graphene.ObjectType):
        class Meta:
            name = "SwapTeamsPayload"
        match = graphene.Field(MatchType)
        success = graphene.Boolean()
        message = graphene.String()

    def mutate(self, info, input):
        match_id = input.match_id
        new_home_team_id = input.new_home_team_id
        new_away_team_id = input.away_team_id

        match = Match.query.get(match_id)
        if not match:
            return SwapTeams.Output(success=False, message=f"Match with ID {match_id} not found.")

        new_home_team = Team.query.get(new_home_team_id)
        new_away_team = Team.query.get(new_away_team_id)

        if not new_home_team or not new_away_team:
            return SwapTeams.Output(success=False, message="One or both new teams not found.")

        if new_home_team_id == new_away_team_id:
            return SwapTeams.Output(success=False, message="New home team and new away team cannot be the same.")

        if check_team_availability(new_home_team_id, match.start_time, match.end_time, exclude_match_id=match_id):
            return SwapTeams.Output(success=False, message=f"New home team '{new_home_team.name}' is already booked during this time slot for other matches.")

        if check_team_availability(new_away_team_id, match.start_time, match.end_time, exclude_match_id=match_id):
            return SwapTeams.Output(success=False, message=f"New away team '{new_away_team.name}' is already booked during this time slot for other matches.")

        match.home_team_id = new_home_team_id
        match.away_team_id = new_away_team_id
        db.session.commit()

        return SwapTeams.Output(
            match=match,
            success=True,
            message=f"Teams swapped successfully for match ID {match_id}."
        )

# ----------------------------------------------------------------------
# mutation root class
# ----------------------------------------------------------------------
class Mutation(graphene.ObjectType):
    create_match = CreateMatch.Field()
    delete_match = DeleteMatch.Field()
    swap_teams = SwapTeams.Field()