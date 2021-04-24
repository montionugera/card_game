from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class CardGame(Base):
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="card_games")
    game_info = Column(JSON)
    open_count = Column(Integer, default=0)


class BestScore(Base):
    id = Column(Integer, primary_key=True, index=True)
    min_open_count = Column(Integer, default=999)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="best_score")
