from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.card_game import CardGame
from app.schemas.game import CardGameCreate, CardGameUpdate, GameInfoInDB


class CRUDCardGame(CRUDBase[CardGame, CardGameCreate, CardGameUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: CardGameCreate, owner_id: int
    ) -> CardGame:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["game_info"] = GameInfoInDB.build_random_game().dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        print("return", db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[CardGame]:
        return (
            db.query(self.model)
            .filter(CardGame.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


game = CRUDCardGame(CardGame)
