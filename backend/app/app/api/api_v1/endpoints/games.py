from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.card_game import BestScore

router = APIRouter()


@router.post("/", response_model=schemas.CardGame)
def create_game(
    *,
    db: Session = Depends(deps.get_db),
    game_in: schemas.CardGameCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new game.
    """
    item = crud.game.create_with_owner(db=db, obj_in=game_in, owner_id=current_user.id)
    return item


@router.post("/{id}/open_card/{card_position}", response_model=schemas.CardGame)
def open_card(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    card_position: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    try to open card with card position 0-11
    """
    card_game = crud.game.get(db=db, id=id)
    if not card_game:
        raise HTTPException(status_code=404, detail="CardGame not found")
    if not crud.user.is_superuser(current_user) and (
        card_game.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    game_info_json = card_game.game_info
    game_info = schemas.game.GameInfoInDB(**game_info_json)
    game_info.accept_answer_if_in_condition(card_position)
    card_game.game_info = game_info.dict()
    card_game.open_count += 1

    # Update Best Score if need
    if game_info.is_game_end():
        best_score = (
            db.query(BestScore).filter(BestScore.user_id == card_game.owner_id).first()
        )
        if best_score is None:
            best_score = BestScore(
                user_id=card_game.owner_id, min_open_count=card_game.open_count
            )
            db.add(best_score)
        if best_score.min_open_count > card_game.open_count:
            best_score.min_open_count = card_game.open_count
    db.commit()

    return card_game


@router.get("/{id}", response_model=schemas.CardGame)
def read_game(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get Game by ID.
    """
    item = crud.game.get(db=db, id=id)

    if not item:
        raise HTTPException(status_code=404, detail="CardGame not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item
