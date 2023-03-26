from database.db_users import check_manga_in_user_target, read_manga_in_target, read_user_in_db_with_user_id
from database.db_update import read_all_update_status_false
from database.db_description import read_descr_for_hash_name


async def user_menu_text(user_id: str):
    user = await read_user_in_db_with_user_id(user_id)
    if user.target is not None:  # and user.target != '':
        manga_count = len(user.target.split(' * '))
    else:
        manga_count = 0
    return f'''Приветствую тебя, {user.fullname}!
    Количество отслеживаемых тобой проектов = {manga_count}!
    Подписка на получение всех обновлений = {'активна' if user.all_target else 'не активна'}.
    Подписка на получение сообщений = {'активна' if user.live_status else 'не активна'}.'''


LEXICON: dict[str, str] = {
    'bad_message_answer': '''На данном этапе развития бота не нашлось применения для отправленного Вами сообщений. Прошу прощения!''',
    '/start':   '''Добро пожаловать на стартовую страницу бота!
    Для ознакомления с целью этого бота и его возможностями выбирай соответствующую кнопку, не кусает :)''',
    '/help': '''Данный бот был создан с целью помочь тебе следить за выходом новых глав твоей любимой манги!

    Обновления отслеживаются с сайта: <b>https://readmanga.live</b>

    Бот находится в режиме бета-тестирования, поэтому возможны отдельные ошибки и неполадки, о которых прошу тебя сообщить мне в обратной связи на <b>(вставить ссылку)</b>. Скриншоты и предложения одобряются :)''',
    'add_manga_page': '''Для добавления манги в список отслеживаемых необходимо:
    1. Перейти на сайт https://readmanga.live
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
    '/help': '''Информацией о боте''',
    '/user_menu': '''Меню пользователя'''
    }


LEXICON_COMMAND_USER_MENU: dict[str, str] = {
    '/settings': '''Настройки пользователя''',
    '/manga_target': '''Список отслеживаемой манги''',
    '/show_update': '''Последние обновления''',
    '/start': '''Вернуться в начало'''
}


LEXICON_COMMAND_READ_MANGA: dict[str, str] = {
    '/manga_add': '''Добавить''',
    '/manga_delete': '''Удалить''',
    '/user_menu': '''Меню пользователя''',
    '/start': '''Вернуться в начало'''
}


LEXICON_SETTINGS: dict[str, str] = {
    '/all_target_false': 'Не получать все обновления!',
    '/all_target_true': 'Получать все обновления сайта!',
    '/status_live_false': 'Не получать сообщения!',
    '/status_live_true': 'Получать сообщения!'
}


# LEXICON_MENU_COMMAND: dict[str, str] = {
#     '/help': 'Информация о боте'
#     }


LEXICON_UPDATE_COMMAND: dict[str, str] = {
    '/review': 'Вывести информацию о проектах',
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


TIME_DELETE = 10
warning_message = f'''\n\nДанное сообщение будет удалено через {TIME_DELETE} секунд!\n\n'''


async def text_manga_target(user_id: int) -> str:
    text = '''Список отслеживаемой манги:\n\n'''
    manga_names_link_list = await read_manga_in_target(user_id)
    if manga_names_link_list is not None:
        for i, name_link_tuple in enumerate(manga_names_link_list, 1):
            text += f'{i}. \t<a href="{URL_MANGA + name_link_tuple[1]}">{name_link_tuple[0]}</a>\n'
    else:
        text += 'На данный момент ты не отслеживаешь ни одного проекта!'
    return text


async def text_manga_list_target(user_id: int) -> list:
    manga_list = await read_manga_in_target(user_id)
    if manga_list is not None:
        return manga_list.split(' * ')
    return None


LEN_UPDATE_LIST: int = 10


async def text_update_manga_for_all(i: int, updates: list):
    text: str = ''
    if updates is not None:
        for j, manga in enumerate(updates, i * LEN_UPDATE_LIST + 1):
            if j == 1:
                text = '''Вышли следующие обновления!\n\n'''
            text += f'\t{j}. {manga.name}\n'
            if manga.chapter_start is None:
                text += 'Обновление вышло без глав!\n'
            elif manga.chapter_end is None:
                text += f'Вышла новая глава:\t{manga.chapter_start}\n'
            else:
                text += f'Вышли новые главы:\tс {manga.chapter_start} по {manga.chapter_end}\n'
            text += '\n'
        return text
    return None


async def group_list_update_manga(updates: list):
    if updates is not None:
        updates_list = []
        for i in range(0, len(updates), LEN_UPDATE_LIST):
            updates_list.append(updates[i: i + LEN_UPDATE_LIST])
        updates = []
        for i, update in enumerate(updates_list, 0):
            update = await text_update_manga_for_all(i, update)
            updates.append(update)
        return updates
    return None


URL_MANGA = 'https://readmanga.live'


async def create_text_review_manga(hash_name: str, user_id: int) -> tuple[str]:
    descr = await read_descr_for_hash_name(hash_name)
    if descr is not None:
        text = f'<b>{descr.name}</b>'
        if descr.users is not None and str(user_id) in descr.users:
            text += '\t\t<i>[Уже в списке!]</i>\n\n'
        else:
            text += '\t\t<i>[Все ещё не списке!]</i>\n\n'
        text += f'Жанры: {descr.genre.lower() if descr.genre else "отсутствуют"}\n\n'
        text += f'Описание:\n\t\t{descr.description if descr.description else "На данный момент отсутствует!"}\n\n'
        text += f'Ссылка для чтения: <a href="{URL_MANGA + descr.link}"> перейти на сайт </a>\n\n'
        return (text[: 1024], descr.image)  # ограничение caption - 1024
