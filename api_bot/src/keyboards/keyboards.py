from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.lexicon.lexicon_ru import (
    LEXICON_SHOW_UPDATE_VIEWER,
    LEXICON_SETTINGS,
    LEXICON_REVIEW_COMMAND_DEL,
    LEXICON_REVIEW_COMMAND,
    LEXICON_UPDATE_COMMAND,
    LEXICON_COMMAND,
    LEXICON_COMMAND_USER_MENU,
    LEXICON_COMMAND_READ_MANGA,
    text_manga_list_target
)
from src.services.hash_all import hash_full_text


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
    user_id: int
):
    manga_list = await text_manga_list_target(user_id)
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
    user_id: int, hash_name: str
):
    if await check_manga_in_user_target(user_id, hash_name):
        lexicon = LEXICON_REVIEW_COMMAND_DEL
    else:
        lexicon = LEXICON_REVIEW_COMMAND
    return InlineKeyboardBuilder(
            [[InlineKeyboardButton(
                text=lexicon[key],
                callback_data=key)] for key in lexicon]
            ).adjust(1, repeat=True).as_markup()


async def manga_settings_kb(user_id: int):
    user = await _get_user(user_id)
    all_target = f'/all_target_{user.all_target}'.lower()
    status = f'/status_live_{user.live_status}'.lower()
    all_target_but = InlineKeyboardButton(
            text=LEXICON_SETTINGS[all_target],
            callback_data=all_target
        )
    status_but = InlineKeyboardButton(
            text=LEXICON_SETTINGS[status],
            callback_data=status
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
