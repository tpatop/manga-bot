from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import (
    Column, Integer, String, JSON, ForeignKey
)


Base = declarative_base()


class Manga(Base):
    __tablename__ = 'manga'

    manga_id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, nullable=False)
    link = Column(String, nullable=False)
    name = Column(String)
    users = Column(JSON, nullable=True)


class UpdateManga(Base):
    __tablename__ = 'manga_updates'

    update_manga_id = Column(Integer, primary_key=True, autoincrement=True)
    manga_id = Column(Integer, ForeignKey('manga.manga_id'))
    chapters = Column(String)
