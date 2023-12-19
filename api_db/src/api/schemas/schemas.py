from pydantic import BaseModel
from pydantic.types import Json


class MangaUpdate(BaseModel):
    url_id: int
    link: str
    chapters: str
    name: str


class UserPydanticModel(BaseModel):
    user_id: int
    settings: Json
    status: bool
