from __future__ import annotations

import random
from typing import Dict, List, Optional

from pydantic import BaseModel, root_validator

from app.core.config import settings


class GameInfoInDB(BaseModel):
    display_by_position: List[str]  # display_by_position
    answer_as_position_in_sequence: List[int]  # positions
    display_by_answer: Dict[int, str]  # positions

    @staticmethod
    def build_random_game() -> GameInfoInDB:
        number_displays = [str(idx + 1) for idx in range(settings.GAME_SIZE)] * 2
        solutions = []
        for _ in [idx for idx in range(settings.GAME_SIZE)] * 2:
            card_display_index = random.choice(range(len(number_displays)))
            card_display = number_displays.pop(card_display_index)
            solutions.append(card_display)
        return GameInfoInDB(
            display_by_position=solutions,
            answer_as_position_in_sequence=[],
            display_by_answer={},
        )

    def should_accept_answer(self, answer_position: int) -> bool:
        if len(self.answer_as_position_in_sequence) == len(self.display_by_position):
            return False
        if len(self.answer_as_position_in_sequence) % 2 == 0:
            return True
        if (
            self.display_by_position[self.answer_as_position_in_sequence[-1]]
            == self.display_by_position[answer_position]
        ):
            return True

    def accept_answer_if_in_condition(self, answer_position: int) -> None:
        if self.should_accept_answer(answer_position):
            self.answer_as_position_in_sequence.append(answer_position)
            self.display_by_answer[answer_position] = self.display_by_position[
                answer_position
            ]
        else:
            if len(self.answer_as_position_in_sequence) % 2 == 1:
                self.answer_as_position_in_sequence.pop()

    def is_game_end(self) -> bool:
        return len(self.answer_as_position_in_sequence) == len(self.display_by_position)


# Shared properties
class CardGameBase(BaseModel):
    game_info: GameInfoInDB
    open_count: int = 0


# Properties to receive on CardGame creation
class CardGameCreate(BaseModel):
    pass


# Properties to receive on CardGame update
class CardGameUpdate(CardGameBase):
    pass


# Properties shared by models stored in DB
class CardGameInDBBase(CardGameBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class GameInfo(BaseModel):
    answer_as_position_in_sequence: List[int]
    display_by_answer: Dict[int, str]
    is_game_end: Optional[bool]

    @root_validator
    def validate_date(cls, values):
        values["is_game_end"] = (
            len(values["answer_as_position_in_sequence"]) == settings.GAME_SIZE * 2
        )
        return values


# Properties to return to client
class CardGame(CardGameInDBBase):
    game_info: GameInfo


# Properties properties stored in DB
class CardGameInDB(CardGameInDBBase):
    pass


class BestScore(BaseModel):
    id: int
    user_id: int
    min_open_count: int

    class Config:
        orm_mode = True
