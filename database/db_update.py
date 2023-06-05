import time
import sqlalchemy
from time import sleep
from random import randint
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, desc
from services.parser import process_start_parsing
from database.db_description import add_description
from .management import DatabaseManagement


SQLITE_BOT_DB = 'bot.db'
engine = None
Session = None
Base = declarative_base()


NUMBER_OF_PAGES: int = 20
UPDATE_QUANTITY: int = 2000


def TIME_SLEEP():
    return randint(1, 5)  # от 1 до 5 секунд задержка


async def create_update_table(database_url: str = SQLITE_BOT_DB):
    '''Функция создает БД и таблицу, если их ещё нет'''
    global engine, Session, Update
    # создание синхронного движка, 1 движок - 1 БД
    engine = sqlalchemy.create_engine(f'sqlite:///{database_url}')
    # создание базовой модели
    Base.metadata.create_all(engine)
    # создаем модель, объекты которой будут храниться в бд

    class Update(Base):
        # сопоставление класса с определенной таблицей в БД
        __tablename__ = 'update'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String)
        chapter_start = Column(String, nullable=True)
        chapter_end = Column(String, nullable=True)
        status = Column(Boolean, default=False)
    # создание класса сессии
    Session = sessionmaker(bind=engine)
    # создание таблицы
    conn = engine.connect()
    Base.metadata.create_all(conn)
    conn.close()


async def process_clean_db_update_not_all(session: Session) -> Session:
    '''Функция удаляет старые записи из БД, согласно ограничению в UPDATE_QUANTITY'''
    quantity = session.query(Update).count()
    if quantity > UPDATE_QUANTITY:
        excess = quantity - UPDATE_QUANTITY
        to_delete = session.query(Update).order_by(Update.id.asc()).limit(excess).all()
        for update in to_delete:
            session.delete(update)
        session.commit()
    return session


async def process_check_chapters(chapters: list[str]) -> bool:
    check_list = ['экстра', 'сингл']
    for word in check_list:
        if word in ''.join(chapters).lower():
            return True
    return False


async def process_combining_values(session: Session) -> Session:
    '''Функция выполняет добавление в БД обновленного мультистраничного элемента
        запроса, игнорируя те, что были отработаны ранее (status==True)
        и встречающиеся в БД лишь единожды. После добавления нового элемента
        в БД, обновляет статус использованных для формирования элементов на True'''
    names = [x[0] for x in session.query(Update.name).filter(Update.status == False).distinct()]
    for name in names:
        update = session.query(Update).filter_by(name=name, status=False)
        if update.count() <= 1:
            continue
        else:
            chapters = []
            for data in update:
                chapters.extend([x for x in (data.chapter_start, data.chapter_end) if x is not None])
                data.status = True
            if await process_check_chapters(chapters):
                chapters = sorted(chapters)
            else:
                chapters = sorted(chapters, key=lambda x: tuple(map(float, x.split(' - '))))
            if chapters[0] != chapters[-1]:  # удалить, когда будет решена проблема с независимого от повторения добавления в БД 1го элемента любого опроса
                new_update = Update(name=name, chapter_start=chapters[0], chapter_end=chapters[-1])
                # print((new_update.name, new_update.chapter_start, new_update.chapter_end))  # удалить в релизе функции
                session.add(new_update)
        # print(update[0].name)
        # print(chapters)

    session.commit()
    return session


async def create_result(session: Session, chapters: list, new_update, len_update: int):
    result = None
    match len_update:
        case 0:
            result = session.query(Update).filter(
                Update.name == new_update.name
                ).first()
        case 1:
            result = session.query(Update).filter(
                Update.name == new_update.name,
                Update.chapter_start == chapters[0],
                ).first()
        case 2 | 3:
            result = session.query(Update).filter(
                Update.name == new_update.name,
                Update.chapter_start == chapters[0],
                Update.chapter_end == chapters[-1],
                ).first()
    return result


async def add_update(db_management: DatabaseManagement):  # функция обновления БД обновлений
    '''Функция добавление записей об обновленных проектах'''
    session = Session()
    try:
        flag = False
        updates: list = []  # чисто для костыля, чтобы работала функция db_description
        for page in range(NUMBER_OF_PAGES):
            if flag:
                print('Остановка выполнения кода')
                break
            sleep(TIME_SLEEP())
            print(f'{time.strftime("%H:%M:%S", time.localtime())} - обработка страницы {page + 1}\n')  # удалить (для отладки и проверки работы)
            zipf = await process_start_parsing(page)
            if zipf is None or zipf == []:
                flag = True
                continue
            for update in zipf:
                if update[1] == 0:  # чтобы не было ошибки при появлении подборок
                    continue
                new_update = Update(name=update[0])
                # print(update[0], update[1], len(update[1]))
                if await process_check_chapters(update[1]):  # проверка для случаев наличия слов в обновлении, как 1, так и 2, 3
                    chapters = update[1]
                elif len(update[1]) > 1:
                    chapters = sorted(update[1], key=lambda x: tuple(map(float, x.split(' - '))))  # для правильного расположения обновленных глав
                else:
                    chapters = update[1]
                match len(update[1]):
                    case 1:
                        new_update.chapter_start = chapters[0]
                    case 2 | 3:
                        new_update.chapter_start = chapters[0]
                        new_update.chapter_end = chapters[-1]
                # проверка на повторение в БД
                result = await create_result(session, chapters, new_update, len(update[1]))
                if result:
                    if flag:  # что бы убрать ошибку, возникающую при дублировании конца и начала страниц одним проектом с одинаковыми главами
                        break
                    print(f'Пошли повторения {result.name, result.chapter_start, result.chapter_end}, останавливаю выполнение цикла')
                    flag = True
                else:
                    flag = False
                    session.add(new_update)
                    if update[0] not in list(map(lambda update: update[0], updates)):
                        updates.append(update)
                # print('итерация выполняется')
        session.commit()
        # print('завершение выполнения add_update')
        session = await process_clean_db_update_not_all(session)
    except Exception as e:
        session.rollback()
        print(f'\t\t Произошла ошибка в add_update:\n{e}\n{time.strftime("%H:%M:%S", time.localtime())}')
        raise
    finally:
        session = await process_combining_values(session)
        session.close()
        if updates:
            await add_description(updates, db_management)
            del updates  # не тестировал, в случае ошибок, удалить (15.03.2023 16.41)


async def read_all_update_status_false():
    with Session() as db:
        updates = db.query(Update).filter_by(status=False).all()
        return updates


async def remake_update_status_in_true():
    with Session() as db:
        updates = db.query(Update).filter_by(status=False).all()
        for update in updates:
            update.status = True
        db.commit()


async def process_show_unique_name_in_update(quantity: int):
    with Session() as db:
        return [x[0] for x in db.query(Update.name).distinct().order_by(desc(Update.id)).limit(quantity).all()]


async def process_show_desc_updates_list(quantity: int):
    '''Функция для получения обновления с конца таблицы
        по необходимому количеству уникальных элементов'''
    with Session() as db:
        updates = []
        names = await process_show_unique_name_in_update(quantity)
        for name in names:
            update = db.query(Update).order_by(desc(Update.id)).filter_by(name=name).first()
            if update is not None:
                updates.append(update)
            else:
                print('!!!!!!!!!!!!!!!!!!!!!!!! Какого хуя?')

        return updates
