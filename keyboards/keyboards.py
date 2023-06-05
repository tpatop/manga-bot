from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_SHOW_UPDATE_VIEWER, LEXICON_SETTINGS, LEXICON_REVIEW_COMMAND_DEL, LEXICON_REVIEW_COMMAND, LEXICON_UPDATE_COMMAND, LEXICON_COMMAND, LEXICON_COMMAND_USER_MENU, LEXICON_COMMAND_READ_MANGA
from lexicon.lexicon_ru import text_manga_list_target
from services.hash_all import hash_full_text
from database.db_users import check_manga_in_user_target, _get_user
from database.management import DatabaseManagement

# стартовая клавиатура, вызываемая и для плохих запросах
start_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder(
    [[InlineKeyboardButton(
            text=LEXICON_COMMAND[f'{command}'],
            callback_data=command) for command in LEXICON_COMMAND
        ]
    ]
).adjust(1, repeat=True).as_markup()


user_menu_but = InlineKeyboardButton(
            text=LEXICON_COMMAND['/user_menu'],
            callback_data='/user_menu')


help_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[user_menu_but]]
)


user_menu_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder(
    [[InlineKeyboardButton(
            text=LEXICON_COMMAND_USER_MENU[f'{command}'],
            callback_data=command) for command in LEXICON_COMMAND_USER_MENU
        ]
    ]
).adjust(1, repeat=True).as_markup()


user_read_manga_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder(
    [[InlineKeyboardButton(
            text=LEXICON_COMMAND_READ_MANGA[f'{command}'],
            callback_data=command) for command in LEXICON_COMMAND_READ_MANGA
        ]
    ]
).adjust(2, 1, 1).as_markup()


ADJUST_CONST: int  # размер клавиатуры


async def delete_manga_keyboard(
    user_id: int, db_management: DatabaseManagement
):
    manga_list = await text_manga_list_target(user_id, db_management)
    if manga_list is not None:
        if len(manga_list) > 30:
            ADJUST_CONST = 3
        else:
            ADJUST_CONST = len(manga_list) // 10 + 1
        del_str = 'del*'
        if manga_list is not None:
            kb = InlineKeyboardBuilder(
            [[InlineKeyboardButton(
                text=name,
                callback_data=del_str + await hash_full_text(name))] for name in manga_list  # 1 символ = 2 байта
            ]
    ).adjust(ADJUST_CONST, repeat=True).as_markup()
            kb = list(kb)[0][1]
            kb.append([user_menu_but])
            return InlineKeyboardMarkup(
                inline_keyboard=kb
            )
    else:
        return help_keyboard


update_manga_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder(
    [[InlineKeyboardButton(
            text=LEXICON_UPDATE_COMMAND[command],
            callback_data=command) for command in LEXICON_UPDATE_COMMAND
    ]]
).adjust(1, repeat=True).as_markup()


from aiogram.types import CallbackQuery
KB_WIDTH = 1


async def show_name_review_manga(callback: CallbackQuery):
    '''Функция парсинга текста сообщения для сбора названий манги'''
    text = callback.message.text
    if text:
        text = text.split('\n\n')
        names = []
        for manga in text:
            if '.' not in manga:
                continue
            name = manga[manga.find('. ') + 2: manga.find('\n')]
            names.append(name)
        return names
    return None


async def create_review_manga_kb(callback: CallbackQuery):
    names = await show_name_review_manga(callback)
    if names:
        rew_str = 'rev*'
        buttons = [InlineKeyboardButton(
                text=name,
                callback_data=rew_str + await hash_full_text(name))
                        for name in names]
        return InlineKeyboardBuilder().row(*buttons).add(InlineKeyboardButton(
            text=LEXICON_UPDATE_COMMAND['/del_update'],
            callback_data='/del_update'
            )
).adjust(KB_WIDTH, repeat=True).as_markup()


async def manga_review_kb(
    user_id: int, hash_name: str, db_management: DatabaseManagement
):
    if await check_manga_in_user_target(user_id, hash_name, db_management):
        lexicon = LEXICON_REVIEW_COMMAND_DEL
    else:
        lexicon = LEXICON_REVIEW_COMMAND
    return InlineKeyboardBuilder(
            [[InlineKeyboardButton(
                text=lexicon[key],
                callback_data=key
        )] for key in lexicon]
).adjust(1, repeat=True).as_markup()


async def manga_settings_kb(user_id: int, db_management: DatabaseManagement):
    user = await _get_user(user_id, db_management)
    all_target = user.all_target
    status = user.live_status
    if all_target:
        all_target_but = InlineKeyboardButton(
            text=LEXICON_SETTINGS['/all_target_false'],
            callback_data='/all_target_false'
        )
    else:
        all_target_but = InlineKeyboardButton(
            text=LEXICON_SETTINGS['/all_target_true'],
            callback_data='/all_target_true'
        )
    if status:
        status_but = InlineKeyboardButton(
            text=LEXICON_SETTINGS['/status_live_false'],
            callback_data='/status_live_false'
        )
    else:
        status_but = InlineKeyboardButton(
            text=LEXICON_SETTINGS['/status_live_true'],
            callback_data='/status_live_true'
        )
    user_menu = InlineKeyboardButton(
        text='''Меню пользователя''',
        callback_data='/user_menu'
        )
    return InlineKeyboardMarkup(inline_keyboard=[
        [all_target_but],
        [status_but],
        [user_menu]
    ])


last_update_review_kb: InlineKeyboardBuilder = InlineKeyboardBuilder(
    [[InlineKeyboardButton(
        text=value,
        callback_data=key) for key, value in LEXICON_SHOW_UPDATE_VIEWER.items()
    ]]
).add(user_menu_but).adjust(2, 2, 1).as_markup()


#         return InlineKeyboardMarkup(
#             inline_keyboard=[[InlineKeyboardButton(
#                 text=name,
#                 callback_data=rew_str + await hash_full_text(name))] for name in names
#             ]
# )

# # стартовая клавиатура
# start_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder(
#     [
#         [InlineKeyboardButton(
#             text=LEXICON_COMMAND[f'{command}'],
#             callback_data=command) for command in LEXICON_COMMAND]
#     ]
# ).adjust(1, repeat=True).as_markup()


# cancel_button: InlineKeyboardButton = InlineKeyboardButton(
#     text=LEXICON['/cancel'],
#     callback_data='/cancel'
# )


# write_url_button = InlineKeyboardButton(
#     text=LEXICON['/write_url'],
#     callback_data='/write_url'
# )


# url_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder(
#     [
#         [InlineKeyboardButton(
#            text=f'Открыть сайт: {name}.',
#             url=url) for name, url in LEXICON_URL.items()]
#     ]
# ).add(write_url_button, cancel_button).adjust(1, repeat=True).as_markup()


# cancel_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
#     inline_keyboard=[[cancel_button]]
# )
