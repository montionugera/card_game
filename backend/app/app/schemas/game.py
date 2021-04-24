from pydantic import BaseModel


# Shared properties
class CardGameBase(BaseModel):
    pass


# Properties to receive on CardGame creation
class CardGameCreate(CardGameBase):
    title: str


# Properties to receive on CardGame update
class CardGameUpdate(CardGameBase):
    pass


# Properties shared by models stored in DB
class CardGameInDBBase(CardGameBase):
    id: int
    title: str
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class CardGame(CardGameInDBBase):
    pass


# Properties properties stored in DB
class CardGameInDB(CardGameInDBBase):
    pass
