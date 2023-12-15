from pydantic import BaseModel


class MangaUpdate(BaseModel):
    url_id: int
    link: str
    chapters: str
    name: str
