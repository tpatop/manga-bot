from pydantic import BaseModel


class UpdateManga(BaseModel):
    url_id: int
    link: str
    chapters: str
    name: str
