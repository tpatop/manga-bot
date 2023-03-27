import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime
# from services.dowload_html import process_download_html
from services.parser import process_manga_add_parsing
from database.db_description import read_manga_in_target_name, del_user_in_manga_decr_db, check_manga_in_db, add_description, add_user_in_manga_decr_db
from services.hash_all import hash_full_text


'''https://metanit.com/python/database/3.1.php'''


SQLITE_BOT_DB = 'bot.db'
engine = None
Session = None
Base = declarative_base()


async def create_user_table(database_url: str = SQLITE_BOT_DB):
    global engine, Session, User
    # создание синхронного движка, 1 движок - 1 БД
    engine = sqlalchemy.create_engine(f'sqlite:///{database_url}')
    # создание базовой модели
    Base.metadata.create_all(engine)
    # создаем модель, объекты которой будут храниться в бд

    class User(Base):
        # сопоставление класса с определенной таблицей в БД
        __tablename__ = 'users'

        user_id = Column(Integer, primary_key=True)
        username = Column(String, nullable=True)  # для обратной связи
        fullname = Column(String, nullable=True)  # для обращения
        update_date = Column(DateTime)  # для сравнения времени последнего обращения
        target = Column(String, nullable=True)  # строка с аниме
        all_target = Column(Boolean, default=False)  # широковещательная рассылка всех обновлений
        live_status = Column(Boolean, default=True)  # статус пользователя

    # создание класса сессии
    Session = sessionmaker(bind=engine)
    # создание таблицы
    conn = engine.connect()
    Base.metadata.create_all(conn)
    conn.close()


async def read_user_in_db_with_user_id(user_id: int):
    user_id = int(user_id)
    with Session() as db:
        return db.query(User).filter_by(user_id=user_id).first()


async def change_user_all_target(user_id: int):
    with Session() as db:
        try:
            user = db.query(User).filter_by(user_id=user_id).first()
            user.all_target = not user.all_target
            db.commit()
        except Exception as e:
            db.rollback()
            print("An error occurred while trying to update the user: ", e)


async def change_user_live_status(user_id: int):
    with Session() as db:
        try:
            user = db.query(User).filter_by(user_id=user_id).first()
            user.live_status = not user.live_status
            db.commit()
        except Exception as e:
            db.rollback()
            print("An error occurred while trying to update the user: ", e)


async def remake_list_user_without_all_target(users: list[int]) -> list[int]:
    users_list = []
    with Session() as db:
        for user_id in users:
            result = db.query(User).filter_by(
                user_id=user_id,
                all_target=False,
                live_status=True).first()
            if result:
                users_list.append(user_id)
    if users_list:
        return users_list
    return None


async def check_user_in_db(user_id: int) -> bool:
    user = await read_user_in_db_with_user_id(user_id)
    return user is not None


async def get_all_live_users():
    with Session() as db:
        users = db.query(User).filter_by(live_status=True).all()
        return users


async def get_users_all_target():
    with Session() as db:
        users = db.query(User).filter_by(all_target=True, live_status=True).all()
        return users


async def add_user_in_db(user_data: dict) -> None:
    with Session() as db:
        new_user = User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            fullname=user_data['fullname'],
            update_date=user_data['update_date']
        )
        db.add(new_user)
        db.commit()
        print(f'Добавление пользователя c id = {user_data["user_id"]} завершено!')


async def add_manga_in_user_db(name: str, user_id: int):
    with Session() as db:
        user_db = db.query(User).filter_by(user_id=user_id).first()
        hash_name = await hash_full_text(name)
        if user_db is not None:
            if user_db.target is None:
                user_db.target = hash_name
            elif hash_name not in user_db.target:
                user_db.target += " * " + hash_name

        db.commit()


async def add_manga_in_target(name: str, user_id: int):
    await add_user_in_manga_decr_db(name, user_id)
    await add_manga_in_user_db(name, user_id)


async def add_manga_in_target_with_url(url: str, user_id: int):
    update = await process_manga_add_parsing(url)
    if update is not None:
        # name, image_orig_link, manga_genre, manga_description, manga_link
        name = update[0]
        manga_in_db = await check_manga_in_db(name)
        if not manga_in_db:  # добавляю в БД мангу
            await add_description([update])
        await add_manga_in_target(name, user_id)
        return True
    else:
        return False


async def read_manga_in_target(user_id: int) -> str:
    user = await read_user_in_db_with_user_id(user_id)
    manga_names_link_list = await read_manga_in_target_name(user.target)
    if manga_names_link_list:
        return manga_names_link_list


async def delete_manga_from_target(hash_name: str, user_id: id):
    if 'del*' in hash_name:
        hash_name = hash_name.replace('del*', '')
    with Session() as db:
        user_db = db.query(User).filter_by(user_id=user_id).first()
        if user_db is not None:
            if user_db.target is not None:
                if hash_name in user_db.target:
                    manga_list = user_db.target.split(' * ')
                    del manga_list[manga_list.index(hash_name)]
                    if manga_list != [''] and manga_list != []:
                        user_db.target = ' * '.join(manga_list)
                    else:
                        user_db.target = None
        db.commit()
    await del_user_in_manga_decr_db(hash_name, user_id)


async def check_manga_in_user_target(user_id: int, hash_name: str) -> bool:
    with Session() as db:
        user = db.query(User).filter_by(user_id=int(user_id)).first()
        return True if user.target is not None and hash_name in user.target else False


# async def add_or_update_user_status(data: CallbackQuery | Message):
#     # создаем саму сессию базы данных
#     with Session() as db:

#         user = db.query(User).filter(User.user_id == data.from_user.id).first()

#         if user is not None:
#             if user.fullname != data.from_user.full_name:
#                 user.fullname = data.from_user.full_name
#             if user.username != data.from_user.username:
#                 user.username = data.from_user.username
#             user.last_update_date = data.date
#             user.live = True
#             print(f'\n\tИнформация по пользователю {data.from_user.username}'
#                   'обновлена!\n')

#         else:
#             user = User(
#                 user_id=data.from_user.id,
#                 username=data.from_user.username,
#                 fullname=data.from_user.full_name,
#                 last_update_date=data.date,
#                 live=True)

#             db.add(user)
#             print(f"\n\tПользователь {data.from_user.username} добавлен в БД!")

#         db.commit()


# def user_was_died(data: CallbackQuery | Message):
#     with Session() as db:
#         user = db.query(User).filter(User.user_id == data.from_user.id).first()
#         if user is not None:
#             user.live = False
#             db.commit()
#         # можно вообще его удалить - db.delete(user)


# async def read_all_database(data: Message):
#     with Session() as db:
#         for user in db.query(User).all():
#             await data.answer(
#                 text=f'\t{user.id}. id = {user.user_id}, '
#                 f'@{user.username}, fullname = {user.fullname}\nlast update '
#                 f'date = {user.last_update_date}, {user.live = }')
#         await data.answer(
#             text='Вывод БД пользователей завершен!',
#             reply_markup=start_keyboard)
