from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer
from services.hash_all import hash_full_text
# from database.db_users import remake_list_user_without_all_target

# engine = None
Session = None
Base = declarative_base()


async def create_description_table(engine):
    '''Функция создает БД и таблицу, если их ещё нет'''
    global Session, Description
    # создание базовой модели
    Base.metadata.create_all(engine)
    # создаем модель, объекты которой будут храниться в бд

    class Description(Base):
        # сопоставление класса с определенной таблицей в БД
        __tablename__ = 'description'
        name = Column(String, primary_key=True)  # название на русском
        hash_name = Column(String, unique=True)
        genre = Column(String, nullable=True)  # строка, содержащая жанр
        description = Column(String, nullable=True)  # описание
        image = Column(String, nullable=True)  # ссылка на фото
        link = Column(String)  # ссылка на мангу
        users = Column(String, nullable=True)

    # создание класса сессии
    Session = sessionmaker(bind=engine)
    # создание таблицы
    conn = engine.connect()
    Base.metadata.create_all(conn)
    conn.close()
    # print('СОздание 2 таблицы завершено')
    return engine


async def add_description(updates: list[tuple[str]]):
    # print('\t\tВызвана функция add_description')  # удалить
    # zipf = zip(image_title, chapters, image_orig_link, manga_genre, manga_description, manga_link)
    # print('Вызвана функция add_descr')
    session = Session()
    try:
        # description: list[Description] = []  # для добавления списка объектов
        for update in updates:
            hash_name = await hash_full_text(update[0])
            new_description = Description(
                name=update[0],
                hash_name=hash_name,
                image=update[2],
                genre=', '.join(update[3]),
                description=update[4],
                link=update[5]
            )
            # проверка на наличие в таблице
            result = session.query(Description).filter(
                Description.name == new_description.name
            ).first()
            if result:
                print(f'\t  result игнорирует {new_description.name}')  # удалить
                # continue
            else:
                print(f'\tresult добавляет {new_description.name}')  # удалить
                session.add(new_description)
            # description.append(new_description)
        # session.add_all(description)
        session.commit()
        # del description
    except:
        session.rollback()
        print('Ошибка в add_description')  # изменить на запись в файл с указанием времени
        raise
    finally:
        session.close()


async def check_manga_in_db(name: str) -> bool:
    with Session() as db:
        result = db.query(Description.name).filter_by(name=name).first()
        return result is not None


async def add_user_in_manga_decr_db(name: str, user_id: int):
    with Session() as db:
        descr = db.query(Description).filter_by(name=name).first()
        if descr is not None:
            if descr.users is None:
                descr.users = str(user_id)
            elif str(user_id) not in descr.users:  # проверка на пустоту атрибута
                descr.users += ' * ' + str(user_id)

        db.commit()


async def del_user_in_manga_decr_db(hash_name: str, user_id: int):
    with Session() as db:
        descr = db.query(Description).filter_by(hash_name=hash_name).first()
        if descr is not None:
            if descr.users is not None and str(user_id) in descr.users:  # проверка на пустоту атрибута
                user_list = descr.users.split(' * ')
                del user_list[user_list.index(str(user_id))]
                if user_list != [''] and user_list != []:
                    descr.users = ' * '.join(user_list)
                else:
                    descr.users = None

        db.commit()


async def read_manga_in_target_name(hash_names: str) -> str:
    '''Функция для чтения названия манги по списку target пользователя'''
    if hash_names is not None:
        hash_names = hash_names.split(' * ')
        names_link_list = []
        with Session() as db:
            for hash_name in hash_names:
                manga = db.query(Description).filter_by(hash_name=hash_name).first()
                if manga is not None:
                    name = manga.name
                    link = manga.link
                    names_link_list.append((name, link))
        return names_link_list
    else:
        return None


async def read_users_by_name_manga(name: str) -> list[int]:
    with Session() as db:
        data = db.query(Description).filter_by(name=name).first()
        if data is not None:
            if data.users is not None:
                users = [int(user_id) for user_id in data.users.split(' * ') if user_id]  # получение списка пользователей list[str]
                # # очистка списка от ошибочного добавления пользователя с all_target
                # users = await remake_list_user_without_all_target(users)
                return users
        return None


async def read_descr_for_hash_name(hash_name: str) -> str:
    if hash_name:
        with Session() as db:
            descr = db.query(Description).filter_by(hash_name=hash_name).first()
            return descr


# async def read_hash_for_name_list(names: list[str]) -> list[str]:
#     if not names:
#         return None
#     hash_names = []
#     with Session() as db:
#         for name in names:
#             descr = db.query(Description).filter_by(name=name).first()
#             if descr is not None:
#                 hash_names.append(descr.hash_name)
#     return hash_names