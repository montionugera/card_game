from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.models.card_game import BestScore

router = APIRouter()


@router.get("/", response_model=List[schemas.BestScore])
def read_best_scores(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 1,
    user_id: Optional[int] = None,
) -> Any:
    """
    Retrieve items.
    """
    stmt = db.query(BestScore)
    if user_id is not None:
        stmt = stmt.filter(BestScore.user_id == user_id)
    return stmt.offset(skip).limit(limit).order_by(BestScore.min_open_count)
