from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import (
    Boolean, Column, Integer, String, JSON, ForeignKey
)


Base = declarative_base()


class Manga(Base):
    '''Информация о проектах'''
    __tablename__ = 'manga'

    manga_id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, nullable=False)
    link = Column(String, nullable=False)
    name = Column(String)


class UpdateManga(Base):
    '''Информация об обновлениях'''
    __tablename__ = 'manga_updates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    manga_id = Column(Integer, ForeignKey('manga.manga_id'))
    chapters = Column(String)


class Users(Base):
    '''Информация о пользователях'''
    __tablename__ = 'users'

    telegram_id = Column(Integer, primary_key=True)
    settings = Column(JSON)
    status = Column(Boolean, default=True)


class AdapterUserManga(Base):
    '''Пары пользователь-манга для упрощения процессов'''
    __tablename__ = 'user_manga'

    user = Column(Integer, ForeignKey('users.telegram_id'), primary_key=True)
    manga = Column(Integer, ForeignKey('manga.manga_id'), primary_key=True)
