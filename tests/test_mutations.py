import pytest
from app import create_app 
from models import db
from schema import schema 
from models.team import Team
from models.match import Match
from datetime import datetime, timedelta
from graphene.test import Client

@pytest.fixture
def client():
    app_instance = create_app()
    app_instance.config['TESTING'] = True 

    with app_instance.app_context(): 
        db.create_all() 
        team1 = Team(name="Test Team A")
        team2 = Team(name="Test Team B")
        team3 = Team(name="Test Team C")
        team4 = Team(name="Test Team D")
        db.session.add_all([team1, team2, team3, team4])
        db.session.commit()
        yield Client(schema) 
        db.session.remove() 
        db.drop_all()


def test_create_match_success(client):
    query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1,
                awayTeamId: 2,
                startTime: "2025-08-01T10:00:00",
                endTime: "2025-08-01T12:00:00"
            }) {
                match {
                    id
                    homeTeam { name }
                    awayTeam { name }
                }
                success
                message
            }
        }
    """
    result = client.execute(query)

    assert result['data']['createMatch']['success'] is True
    assert result['data']['createMatch']['match']['homeTeam']['name'] == "Test Team A"
    assert result['data']['createMatch']['match']['awayTeam']['name'] == "Test Team B"
    assert result['data']['createMatch']['message'] == "Match created successfully!"
    assert result['data']['createMatch']['match']['id'] is not None

# (double-booking)
def test_create_match_conflict(client):
    initial_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1,
                awayTeamId: 2,
                startTime: "2025-08-01T10:00:00",
                endTime: "2025-08-01T12:00:00"
            }) {
                success
            }
        }
    """
    client.execute(initial_query) # Executa a primeira partida para criar o conflito

    # Agora, tente criar uma segunda partida para o Team A no mesmo horário
    conflict_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1, # Team A
                awayTeamId: 3, # Team C
                startTime: "2025-08-01T11:00:00", # Horário sobreposto
                endTime: "2025-08-01T13:00:00"
            }) {
                success
                message
            }
        }
    """
    result = client.execute(conflict_query)

    assert result['data']['createMatch']['success'] is False
    assert "is already booked during this time slot" in result['data']['createMatch']['message']
    assert "Test Team A" in result['data']['createMatch']['message']

# Teste para deletar uma partida com sucesso
def test_delete_match_success(client):
    # Crie uma partida para deletar
    create_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1,
                awayTeamId: 2,
                startTime: "2025-08-02T10:00:00",
                endTime: "2025-08-02T12:00:00"
            }) {
                match { id }
                success
            }
        }
    """
    create_result = client.execute(create_query)
    match_id = create_result['data']['createMatch']['match']['id']

    # Delete a partida
    delete_query = f"""
        mutation {{
            deleteMatch(id: {match_id}) {{
                success
                message
            }}
        }}
    """
    delete_result = client.execute(delete_query)

    assert delete_result['data']['deleteMatch']['success'] is True
    assert f"Match with ID {match_id} deleted successfully." in delete_result['data']['deleteMatch']['message']

    # Verifique se a partida realmente foi deletada
    query_after_delete = f"""
        query {{
            matchById(id: {match_id}) {{
                id
            }}
        }}
    """
    check_result = client.execute(query_after_delete)
    assert check_result['data']['matchById'] is None # Deve ser nulo se deletado

def test_delete_match_not_found(client):
    delete_query = """
        mutation {
            deleteMatch(id: 9999) { # ID que certamente não existe
                success
                message
            }
        }
    """
    result = client.execute(delete_query)

    assert result['data']['deleteMatch']['success'] is False
    assert "Match with ID 9999 not found." in result['data']['deleteMatch']['message']

def test_swap_teams_success(client):
    create_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1,
                awayTeamId: 2,
                startTime: "2025-08-03T10:00:00",
                endTime: "2025-08-03T12:00:00"
            }) {
                match { id }
                success
            }
        }
    """
    create_result = client.execute(create_query)
    match_id = create_result['data']['createMatch']['match']['id']

    swap_query = f"""
        mutation {{
            swapTeams(input: {{
                matchId: {match_id},
                newHomeTeamId: 3, # Team C
                newAwayTeamId: 4  # Team D
            }}) {{
                match {{
                    id
                    homeTeam {{ name }}
                    awayTeam {{ name }}
                }}
                success
                message
            }}
        }}
    """
    swap_result = client.execute(swap_query)

    assert swap_result['data']['swapTeams']['success'] is True
    assert swap_result['data']['swapTeams']['match']['homeTeam']['name'] == "Test Team C"
    assert swap_result['data']['swapTeams']['match']['awayTeam']['name'] == "Test Team D"
    assert f"Teams swapped successfully for match ID {match_id}." in swap_result['data']['swapTeams']['message']

def test_swap_teams_conflict(client):
    create_match_A_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1, # Team A
                awayTeamId: 2, # Team B
                startTime: "2025-08-04T10:00:00",
                endTime: "2025-08-04T12:00:00"
            }) {
                match { id }
                success
            }
        }
    """
    create_result_A = client.execute(create_match_A_query)
    match_A_id = create_result_A['data']['createMatch']['match']['id']

    # Crie uma segunda partida que ocupa o Team C no mesmo horário (Partida B)
    create_match_B_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 3, # Team C (estará ocupado)
                awayTeamId: 4, # Team D
                startTime: "2025-08-04T10:30:00", # Horário sobreposto com Partida A
                endTime: "2025-08-04T12:30:00"
            }) {
                success
            }
        }
    """
    client.execute(create_match_B_query)

    # Tente trocar times na Partida A para incluir o Team C (que está ocupado)
    swap_conflict_query = f"""
        mutation {{
            swapTeams(input: {{
                matchId: {match_A_id},
                newHomeTeamId: 3, # Tentar colocar Team C (ocupado)
                newAwayTeamId: 2
            }}) {{
                success
                message
            }}
        }}
    """
    swap_conflict_result = client.execute(swap_conflict_query)

    assert swap_conflict_result['data']['swapTeams']['success'] is False
    assert "is already booked during this time slot for other matches." in swap_conflict_result['data']['swapTeams']['message']
    assert "Test Team C" in swap_conflict_result['data']['swapTeams']['message']

def test_swap_teams_same_new_teams(client):
    create_query = """
        mutation {
            createMatch(input: {
                homeTeamId: 1,
                awayTeamId: 2,
                startTime: "2025-08-05T10:00:00",
                endTime: "2025-08-05T12:00:00"
            }) {
                match { id }
                success
            }
        }
    """
    create_result = client.execute(create_query)
    match_id = create_result['data']['createMatch']['match']['id']

    swap_query = f"""
        mutation {{
            swapTeams(input: {{
                matchId: {match_id},
                newHomeTeamId: 1,
                newAwayTeamId: 1
            }}) {{
                success
                message
            }}
        }}
    """
    swap_result = client.execute(swap_query)

    assert swap_result['data']['swapTeams']['success'] is False
    assert "New home team and new away team cannot be the same." in swap_result['data']['swapTeams']['message']