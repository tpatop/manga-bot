import time
from time import sleep
from random import randint
from services.parser import process_start_parsing
from database.db_description import add_description
from .management import DatabaseManagement, UpdateRepo
from .models import Update


NUMBER_OF_PAGES: int = 20
UPDATE_QUANTITY: int = 20000


def TIME_SLEEP():
    return randint(1, 5)  # от 1 до 5 секунд задержка


async def process_clean_db_update_not_all(db_management: DatabaseManagement):
    '''Удаление старые записи из БД, согласно ограничению в UPDATE_QUANTITY'''
    update_repo: UpdateRepo = db_management.get_update_repo()
    quantity = await update_repo.count_update()
    if quantity > UPDATE_QUANTITY:
        excess = quantity - UPDATE_QUANTITY
        await update_repo.delete_updates(excess)


async def process_check_chapters(chapters: list[str]) -> bool:
    check_list = ['экстра', 'сингл']
    for word in check_list:
        if word in ''.join(chapters).lower():
            return True
    return False


async def read_all_update_status_false(db_management: DatabaseManagement):
    filter = {'status': False}
    updates = await db_management.get_update_repo().get_updates(filter)
    return updates


async def process_combining_values(db_management: DatabaseManagement):
    '''Функция добавления в БД обновленного мультистраничного элемента
        запроса, игнорируя те, что были отработаны ранее (status==True)
        и встречающиеся в БД лишь единожды. После добавления нового элемента
        в БД, обновляет статус использованных элементов на True'''
    result_list = []
    update_repo: UpdateRepo = db_management.get_update_repo()
    updates = await read_all_update_status_false(db_management)
    names = await update_repo.get_unique_name_update(updates=updates)
    for name in names:
        filter = {'name': name, 'status': False}
        update = await update_repo.get_updates(filter)
        if len(update) >= 2:
            chapters = []
            for data in update:
                chapters.extend([x for x in (data.chapter_start, data.chapter_end) if x is not None])
                chapters = list(set(chapters))
                data.status = True
            await update_repo.create_or_update_updates(update)
            if await process_check_chapters(chapters):
                chapters = sorted(chapters)
            else:
                chapters = sorted(
                    chapters,
                    key=lambda x: tuple(map(float, x.split(' - ')))
                )
            if chapters:
                new_update = Update(name=name,
                                    chapter_start=chapters[0])
                if chapters[0] != chapters[-1]:
                    new_update.chapter_end = chapters[-1]
                result_list.append(new_update)
    await update_repo.create_or_update_updates(result_list)


async def cheaking_for_repetition(
        db_management: DatabaseManagement,
        chapters: list,
        new_update: Update,
        len_update: int
):
    update_repo: UpdateRepo = db_management.get_update_repo()
    match len_update:
        case 0:
            filter = {'name': new_update.name,
                      'chapter_start': None,
                      'chapter_end': None}
        case 1:
            filter = {'name': new_update.name,
                      'chapter_start': chapters[0],
                      'chapter_end': None}
        case 2 | 3:
            filter = {'name': new_update.name,
                      'chapter_start': chapters[0]}
            if chapters[0] != chapters[-1]:
                filter['chapter_end'] = chapters[-1]
            else:
                filter['chapter_end'] = None

    result = await update_repo.get_updates(filter)
    return result[0] if result else None


async def responce_error(exc):
    with open('errors.txt', 'a', encoding='UTF-8') as file:
        print(f'\t\t Произошла ошибка в add_update:\n{exc}\n',
              f'{time.strftime("%H:%M:%S", time.localtime())}', file=file)


async def add_update(number_url: int, db_management: DatabaseManagement):
    '''Функция добавление записей обновлений проектов'''
    update_repo: UpdateRepo = db_management.get_update_repo()
    try:
        flag = False
        # чисто для костыля, чтобы работала функция db_description
        updates: list = []
        update_list: list[Update] = []
        for page in range(NUMBER_OF_PAGES):
            if flag:
                print('Остановка выполнения кода')
                break
            sleep(TIME_SLEEP())
            # удалить (для отладки и проверки работы)
            print(f'{time.strftime("%H:%M:%S", time.localtime())}',
                  f'- обработка страницы {page + 1}\n')
            zipf = await process_start_parsing(number_url, page)
            if zipf is None or zipf == []:
                flag = True
                continue
            for update in zipf:
                # чтобы не было ошибки при появлении подборок
                if update[1] == 0:
                    continue
                new_update = Update(name=update[0])
                chapters = list(set(update[1]))
                # проверка наличия слов в обновлении, как 1, так и 2, 3
                if await process_check_chapters(update[1]):
                    chapters = chapters
                elif len(update[1]) > 1:
                    # для правильного расположения обновленных глав
                    chapters = sorted(
                        chapters,
                        key=lambda x: tuple(map(float, x.split(' - ')))
                    )
                else:
                    chapters = chapters
                match len(chapters):
                    case 1:
                        new_update.chapter_start = chapters[0]
                    case 2 | 3:
                        new_update.chapter_start = chapters[0]
                        if chapters[0] != chapters[-1]:
                            new_update.chapter_end = chapters[-1]
                # проверка на повторение в БД
                result = await cheaking_for_repetition(
                    db_management, chapters, new_update, len(chapters))
                if result is not None:
                    # что бы убрать ошибку, возникающую при дублировании конца
                    # и начала страниц одним проектом с одинаковыми главами
                    if flag:
                        break
                    print('Пошли повторения')
                    flag = True
                else:
                    flag = False
                    update_list.append(new_update)
                    if update[0] not in list(map(lambda upd: upd[0], updates)):
                        updates.append(update)
        await update_repo.create_or_update_updates(update_list)
        await process_clean_db_update_not_all(db_management)
    except Exception as e:
        await responce_error(e)
        raise
    finally:
        await process_combining_values(db_management)
        if updates:
            await add_description(updates, db_management)
            del updates


async def remake_update_status_in_true(db_management: DatabaseManagement):
    updates = await read_all_update_status_false(db_management)
    if updates:
        for upd in updates:
            upd.status = True
        await db_management.get_update_repo().create_or_update_updates(updates)


async def process_show_desc_updates_list(
    quant: int, db_management: DatabaseManagement
):
    '''Функция для получения обновления с конца таблицы
        по необходимому количеству уникальных элементов'''
    updates = []
    update_repo = db_management.get_update_repo()
    names = await update_repo.get_unique_name_update(quant)
    for name in names:
        filter = {'name': name}
        update = await update_repo.get_updates(filter)
        updates.append(update[-1])
    return updates
