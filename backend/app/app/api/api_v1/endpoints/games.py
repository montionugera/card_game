from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.card_game import BestScore

router = APIRouter()


@router.get("/", response_model=List[schemas.CardGame])
def read_games(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    if crud.user.is_superuser(current_user):
        items = crud.game.get_multi(db, skip=skip, limit=limit)
    else:
        items = crud.game.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return items


@router.post("/", response_model=schemas.CardGame)
def create_game(
    *,
    db: Session = Depends(deps.get_db),
    game_in: schemas.CardGameCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = crud.game.create_with_owner(db=db, obj_in=game_in, owner_id=current_user.id)
    return item


@router.post("/{id}/open_card/{card_pos}", response_model=schemas.CardGame)
def open_card(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    card_pos: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    try to open card
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
    game_info.accept_answer_if_in_condition(card_pos)
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
    Get item by ID.
    """
    item = crud.game.get(db=db, id=id)

    if not item:
        raise HTTPException(status_code=404, detail="CardGame not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item
