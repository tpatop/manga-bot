from database.db_users import read_manga_in_target, _get_user
from database.db_description import _get_description
from lexicon.const_url import URL_MANGA
from database.management import DatabaseManagement
from services.hash_all import hash_full_text


async def user_menu_text(user_id: str, db_management: DatabaseManagement):
    user = await _get_user(user_id, db_management)
    if user.target is not None:  # and user.target != '':
        manga_count = len(user.target.split(' * '))
    else:
        manga_count = 0
    return f'''Приветствую тебя, {user.fullname}!
    Ты отслеживаешь <u><b>{manga_count}</b></u> проектов!
    Ты {('не подписан', 'подписан')[user.all_target]} на массовую рассылку обновлений.
    Бот {('не может', 'может')[user.live_status]} отправлять тебе рассылку.'''


LEXICON: dict[str, str] = {
    'bad_message_answer': '''На данном этапе развития бота не нашлось применения для отправленного Вами сообщений. Прошу прощения!''',
    '/start':   '''Добро пожаловать на стартовую страницу бота!
    Для ознакомления с целью этого бота и его возможностями выбирай соответствующую кнопку, не кусает :)''',
    '/help': f'''Данный бот был создан с целью помочь тебе следить за выходом новых глав твоей любимой манги!

    Обновления отслеживаются с сайтов: <b>{', '.join(URL_MANGA)}</b>

    Бот находится в режиме тестирования, поэтому возможны отдельные ошибки и неполадки, о которых прошу тебя сообщить мне в обратной связи на <b>@my_bot_helper</b>. Скриншоты и предложения одобряются :)''',
    'add_manga_page': f'''Для добавления манги в список отслеживаемых необходимо:
    1. Перейти на один из сайтов: {', '.join(URL_MANGA)}
    2. Найти мангу, которую Вы хотите добавить в отслеживаемые
    3. Скопировать ссылку
    4. Отправить ссылку на мангу в данной форме
    5. Ждать обновлений! :)''',
    'delete_manga_page': '''Для удаления манги из списка отслеживаемых необходимо:
    1. Нажать на кнопку, соответствующую названию манги
    2. Дождаться обработки команд и обновления списка
    3. Продолжать пользоваться ботом :)''',
    'successful_add': 'Данная манга успешно добавлена!',
    'successful_del': 'Данная манга успешно удалена из списка!',
    'show_update': '''Для отображения последних обновлений тебе необходимо:
    1. Нажать на кнопку, соответствующую необходимому количеству
    2. Дождаться обработки команд и появления списка
    3. Продолжать пользоваться ботом :)

    Однако будь внимателен: большее количество дублирует меньшее!''',
    'settings_menu': 'Доступно для редактирования:\n'
    }


# для стартовой, дб не очень крупными, под размеры кнопки
LEXICON_COMMAND: dict[str, str] = {
    '/help': '''❓Информацией о боте''',
    '/user_menu': '''Меню пользователя'''
    }


LEXICON_COMMAND_USER_MENU: dict[str, str] = {
    '/settings': '''🛠Настройки пользователя''',
    '/manga_target': '''Список отслеживаемой манги''',
    '/show_update': '''Последние обновления''',
    '/start': '''🔚Вернуться в начало'''
}


LEXICON_COMMAND_READ_MANGA: dict[str, str] = {
    '/manga_add': '''➕Добавить''',
    '/manga_delete': '''🗑Удалить''',
    '/user_menu': '''🔙Меню пользователя''',
    '/start': '''🔚Вернуться в начало'''
}


LEXICON_SETTINGS: dict[str, str] = {
    '/all_target_false': '✅Получать все обновления сайта!',
    '/all_target_true': '❌Не получать все обновления!',
    '/status_live_false': '✅Получать сообщения!',
    '/status_live_true': '❌Не получать сообщения!'
}


# LEXICON_MENU_COMMAND: dict[str, str] = {
#     '/help': 'Информация о боте'
#     }


LEXICON_UPDATE_COMMAND: dict[str, str] = {
    '/review': 'Информация о проектах',
    '/del_update': 'Удалить рассылку'
}


LEXICON_REVIEW_COMMAND_DEL: dict[str, str] = {
    '/del_manga_in_target': 'Удалить мангу из отслеживаемых',
    '/del_update': 'Удалить описание'
}


LEXICON_REVIEW_COMMAND: dict[str, str] = {
    '/add_manga_in_target': 'Добавить мангу в отслеживаемые',
    '/del_update': 'Удалить описание'
}


LEXICON_SHOW_UPDATE_VIEWER: dict[str, str] = {
    '/showup* 5': '5 обновлений',
    '/showup* 10': '10 обновлений',
    '/showup* 20': '20 обновлений',
    '/showup* 30': '30 обновлений',
}


TIME_DELETE = 5
warning_message = f'''\n\nДанное сообщение будет удалено через {TIME_DELETE} секунд!\n\n'''


async def text_manga_target(
    user_id: int, db_management: DatabaseManagement
) -> str:
    text = '''Список отслеживаемой манги:\n\n'''
    manga_names_link_list = await read_manga_in_target(user_id, db_management)
    if manga_names_link_list is not None:
        for i, name_link_tuple in enumerate(manga_names_link_list, 1):
            text += f'{i}. \t<a href="{name_link_tuple[1]}">{name_link_tuple[0]}</a>\n'
    else:
        text += 'На данный момент ты не отслеживаешь ни одного проекта!'
    return text


async def text_manga_list_target(
        user_id: int, db_management: DatabaseManagement
) -> list[tuple[str, str]]:
    manga_list = await read_manga_in_target(user_id, db_management)
    if manga_list is not None:
        manga_name = [manga_tuple[0] for manga_tuple in manga_list]
        return manga_name
    return None


LEN_UPDATE_LIST: int = 10


async def text_update_manga_for_all(
        i: int, updates: list,
        db_management: DatabaseManagement
):
    text: str = ''
    if updates is not None:
        for j, manga in enumerate(updates, i * LEN_UPDATE_LIST + 1):
            if j == 1:
                text = '''Вышли обновления:\n\n'''
            descr = await _get_description(
                await hash_full_text(manga.name),
                db_management
            )
            link = descr.link
            text += f'\t{j}. <a href="{link}">{manga.name}</a>\n'
            if manga.chapter_start is None:
                text += 'Без глав!\n'
            elif manga.chapter_end is None:
                text += f'Новая глава:\t{manga.chapter_start}\n'
            else:
                text += f'Новые главы:\tс {manga.chapter_start} по {manga.chapter_end}\n'
            text += '\n'
        return text
    return None


async def group_list_update_manga(
        updates: list,
        db_management: DatabaseManagement
):
    if updates is not None:
        updates_list = []
        for i in range(0, len(updates), LEN_UPDATE_LIST):
            updates_list.append(updates[i: i + LEN_UPDATE_LIST])
        updates = []
        for i, update in enumerate(updates_list, 0):
            update = await text_update_manga_for_all(i, update, db_management)
            updates.append(update)
        return updates
    return None


async def create_text_review_manga(
    hash_name: str, user_id: int, db_management: DatabaseManagement
) -> tuple[str]:
    descr = await _get_description(hash_name, db_management)
    if descr is not None:
        text = f'<b>{descr.name}</b>'
        if descr.users is not None and str(user_id) in descr.users:
            text += '\t\t<i>[Уже в списке!]</i>\n\n'
        else:
            text += '\t\t<i>[Все ещё не списке!]</i>\n\n'
        text += f'Жанры: {descr.genre.lower() if descr.genre else "отсутствуют"}\n\n'
        text += f'Описание:\n\t\t{descr.description if descr.description else "На данный момент отсутствует!"}\n\n'
        text += f'Ссылка для чтения: <a href="{descr.link}"> перейти на сайт </a>\n\n'
        return (text[: 1024], descr.image)  # ограничение caption - 1024
