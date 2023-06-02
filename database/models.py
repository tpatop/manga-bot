from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime
)

Base = declarative_base()
METADATA = Base.metadata


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)  # для обратной связи
    fullname = Column(String, nullable=True)  # для обращения
    update_date = Column(DateTime)  # для сравнения времени последнего обращения
    target = Column(String, nullable=True)  # строка с аниме
    all_target = Column(Boolean, default=False)  # широковещательная рассылка всех обновлений
    live_status = Column(Boolean, default=True)


class Update(Base):
    __tablename__ = 'update'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    chapter_start = Column(String, nullable=True)
    chapter_end = Column(String, nullable=True)
    status = Column(Boolean, default=False)


class Description(Base):
    __tablename__ = 'description'

    name = Column(String, primary_key=True)  # название на русском
    hash_name = Column(String, unique=True)
    genre = Column(String, nullable=True)  # строка, содержащая жанр
    description = Column(String, nullable=True)  # описание
    image = Column(String, nullable=True)  # ссылка на фото
    link = Column(String)  # ссылка на мангу
    users = Column(String, nullable=True)
