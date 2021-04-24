from collections import defaultdict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.core.config import settings
from app.models import CardGame
from app.schemas import CardGame as CardGameAPIModel
from app.schemas import GameInfoInDB
from app.schemas.game import GAME_SIZE


def test_open_card_til_game_end_data_should_success(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # Create
    data = {}
    response = client.post(
        f"{settings.API_V1_STR}/games/",
        headers=superuser_token_headers,
        json=data,
    )
    card_game = CardGameAPIModel(**response.json())
    card_game_db_model: CardGame = db.query(CardGame).get(card_game.id)
    game_info = GameInfoInDB(**card_game_db_model.game_info)
    position_by_display = defaultdict(list)
    [
        position_by_display[display].append(pos)
        for pos, display in enumerate(game_info.display_by_position)
    ]
    mistake_count = 8
    for i in range(mistake_count):
        pos1, _ = position_by_display["1"]
        pos2, _ = position_by_display["2"]
        client.post(
            f"{settings.API_V1_STR}/games/{card_game.id}/open_card/{pos1}",
            headers=superuser_token_headers,
            json=data,
        )
        client.post(
            f"{settings.API_V1_STR}/games/{card_game.id}/open_card/{pos2}",
            headers=superuser_token_headers,
            json=data,
        )
    for i in range(GAME_SIZE):
        pos1, pos2 = position_by_display[str(i + 1)]
        client.post(
            f"{settings.API_V1_STR}/games/{card_game.id}/open_card/{pos1}",
            headers=superuser_token_headers,
            json=data,
        )
        response = client.post(
            f"{settings.API_V1_STR}/games/{card_game.id}/open_card/{pos2}",
            headers=superuser_token_headers,
            json=data,
        )
    assert response.status_code == 200
    card_game = CardGameAPIModel(**response.json())
    assert len(card_game.game_info.answer_as_position_in_sequence) == GAME_SIZE * 2
    assert len(card_game.game_info.display_by_answer) == GAME_SIZE * 2
    assert card_game.open_count == mistake_count * 2 + GAME_SIZE * 2
    assert card_game.game_info.is_game_end is True
