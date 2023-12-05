import asyncio
from aiogram import Router, Bot
from aiogram.filters import Text, CommandStart
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import (
    group_list_update_manga,
    create_text_review_manga,
    warning_message,
    TIME_DELETE,
    LEXICON,
    user_menu_text,
    text_manga_target
)
from keyboards.keyboards import (
    update_manga_keyboard,
    last_update_review_kb,
    manga_settings_kb,
    manga_review_kb,
    create_review_manga_kb,
    delete_manga_keyboard,
    user_read_manga_keyboard,
    start_keyboard,
    help_keyboard,
    user_menu_keyboard
)
from database.db_users import (
    change_user_live_status,
    change_user_all_target,
    add_manga_in_target,
    add_manga_in_target_with_url,
    delete_manga_from_target
)
from database.db_update import process_show_desc_updates_list
from lexicon.const_url import URL_MANGA
from services.hash_all import hash_full_text
from services.get_readmanga import (
    bot_send_statistic,
    bot_send_to_all_user_live
)

router: Router = Router()


# Приветствие и открытие начальной страницы /start
@router.message(CommandStart())
async def process_start_command(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await message.answer(
        text=LEXICON['/start'],
        reply_markup=start_keyboard
    )


@router.callback_query(Text(text='/start'))
async def process_start_command_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['/start'],
        reply_markup=start_keyboard
    )


######################################################################


@router.callback_query(Text(text='/help'))
async def process_help_command(callback: CallbackQuery, **kwargs):

    await callback.message.edit_text(
        text=LEXICON['/help'],
        reply_markup=help_keyboard
    )


@router.callback_query(Text(text='/user_menu'))
async def process_user_menu_start(callback: CallbackQuery, **kwargs):
    db_management = kwargs.get('database_management')
    text = await user_menu_text(callback.from_user.id, db_management)
    await callback.message.edit_text(
        text=text,
        reply_markup=user_menu_keyboard
    )


######################################################################
# работа с БД


@router.callback_query(Text(text='/manga_add'))
async def process_add_manga_in_target_page(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['add_manga_page'],
        reply_markup=start_keyboard
    )


# добавление в отслеживаемые с помощью ссылки
@router.message(Text(startswith=f'{URL_MANGA[0]}/'))
@router.message(Text(startswith=f'{URL_MANGA[1]}/'))
@router.message(Text(startswith=f'{URL_MANGA[2]}/'))
async def process_add_manga_in_target_with_url(
        message: Message, bot: Bot, **kwargs
):
    db_management = kwargs.get('database_management')
    result = await add_manga_in_target_with_url(
        message.text, message.from_user.id, db_management)

    await message.delete()
    if result:
        await message.answer(
            text=LEXICON['successful_add'] + warning_message
        )
        await asyncio.sleep(TIME_DELETE)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id + 1)
    else:
        await message.answer(
            text='''Произошла ошибка при добавлении!
Возможно, ты ввел неправильный адрес манги!''' + warning_message
        )
        await asyncio.sleep(TIME_DELETE)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id + 1)


@router.callback_query(Text(text='/manga_target'))
async def process_answer_target_manga_for_user(
    callback: CallbackQuery, bot: Bot, **kwargs
):
    db_management = kwargs.get('database_management')
    text = await text_manga_target(callback.from_user.id, db_management)
    await callback.message.edit_text(
        text=text,
        reply_markup=user_read_manga_keyboard)


@router.callback_query(Text(text='/manga_delete'))
async def process_show_manga_in_target_page(callback: CallbackQuery, **kwargs):
    db_management = kwargs.get('database_management')
    kb = await delete_manga_keyboard(callback.from_user.id, db_management)
    await callback.message.edit_text(
        text=LEXICON['delete_manga_page'],
        reply_markup=kb
    )


@router.callback_query(Text(startswith='del*'))
async def process_delete_manga_from_target(callback: CallbackQuery, **kwargs):
    db_management = kwargs.get('database_management')
    await delete_manga_from_target(
        callback.data, callback.from_user.id, db_management)
    kb = await delete_manga_keyboard(callback.from_user.id, db_management)
    await callback.message.edit_reply_markup(
        reply_markup=kb
    )


@router.callback_query(Text(text='/del_update'))
async def process_delete_manga_from_update(callback: CallbackQuery):
    await callback.message.delete()


# для вывода самой клавиатуры с названиями
@router.callback_query(Text(text='/review'))
async def process_show_review_list(callback: CallbackQuery):
    await callback.message.edit_text(
        text='''Список манги для просмотра обновлений:\n\n''',
        reply_markup=await create_review_manga_kb(callback)
    )


# обработка нажатия на клавиатуру с названием для показа описания
@router.callback_query(Text(startswith='rev*'))
async def process_show_review_manga(callback: CallbackQuery, **kwargs):
    db_management = kwargs.get('database_management')
    hash_name = callback.data[4:]
    text, photo = await create_text_review_manga(
        hash_name, callback.from_user.id, db_management
    )
    markup = await manga_review_kb(
        callback.from_user.id, hash_name, db_management)
    await callback.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=markup,
        parse_mode='html'
    )
    await callback.answer()


# добавление в отслеживаемые с помощью инлайн-клавиатуры
@router.callback_query(Text(text='/add_manga_in_target'))
async def process_add_manga_in_target_callback(
    callback: CallbackQuery, bot: Bot, **kwargs
):
    db_management = kwargs.get('database_management')
    name = callback.message.caption
    name = name[: name.find('[')].strip()  # получил название
    hash_name = await hash_full_text(name)
    await add_manga_in_target(
        name, callback.message.chat.id, db_management)
    await bot.answer_callback_query(callback.id,
                                    text=LEXICON['successful_add'],
                                    show_alert=False)
    text, _ = await create_text_review_manga(
        hash_name, callback.from_user.id, db_management
    )
    markup = await manga_review_kb(
        callback.from_user.id, hash_name, db_management)
    await callback.message.edit_caption(
        caption=text,
        reply_markup=markup
    )


# обратное действие (удаление из списка)
@router.callback_query(Text(text='/del_manga_in_target'))
async def process_del_manga_in_target_callback(
    callback: CallbackQuery, bot: Bot, **kwargs
):
    db_management = kwargs.get('database_management')
    name = callback.message.caption
    name = name[: name.find('[')].strip()  # получил название
    hash_name = await hash_full_text(name)
    await delete_manga_from_target(
        hash_name, callback.message.chat.id, db_management)
    await bot.answer_callback_query(callback.id,
                                    text=LEXICON['successful_del'],
                                    show_alert=False)
    text, _ = await create_text_review_manga(
        hash_name, callback.from_user.id, db_management
    )
    markup = await manga_review_kb(
        callback.from_user.id, hash_name, db_management)
    await callback.message.edit_caption(
        caption=text,
        reply_markup=markup
    )


@router.callback_query(Text(text='/settings'))
async def show_settings_for_user(callback: CallbackQuery, **kwargs):
    db_management = kwargs.get('database_management')
    markup = await manga_settings_kb(callback.from_user.id, db_management)
    await callback.message.edit_text(
        text=LEXICON['settings_menu'],
        reply_markup=markup
    )

# '/all_target_false': 'Обновления из списка',
# '/all_target_true': 'Все обновления сайта',
# '/status_live_true': 'Не получать обновления!',
# '/status_live_false': 'Получать обновления!'


@router.callback_query(Text(text='/all_target_true'))
@router.callback_query(Text(text='/all_target_false'))
async def process_all_target_user_change(
    callback: CallbackQuery, **kwargs
):
    db_management = kwargs.get('database_management')
    await change_user_all_target(callback.from_user.id, db_management)
    markup = await manga_settings_kb(callback.from_user.id, db_management)
    await callback.message.edit_reply_markup(
        text=LEXICON['settings_menu'],
        reply_markup=markup
    )


@router.callback_query(Text(text='/status_live_true'))
@router.callback_query(Text(text='/status_live_false'))
async def process_user_status_live_change(
    callback: CallbackQuery, **kwargs
):
    db_management = kwargs.get('database_management')
    await change_user_live_status(callback.from_user.id, db_management)
    markup = await manga_settings_kb(callback.from_user.id, db_management)
    await callback.message.edit_reply_markup(
        text=LEXICON['settings_menu'],
        reply_markup=markup
    )


@router.callback_query(Text(text='/show_update'))
async def process_show_menu_update_viewer(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['show_update'],
        reply_markup=last_update_review_kb
    )


# показ обновлений 5-30
@router.callback_query(Text(startswith='/showup*'))
async def process_show_update_viewer(callback: CallbackQuery, **kwargs):
    db_management = kwargs.get('database_management')
    quantity = int(callback.data.split()[1])
    updates = await process_show_desc_updates_list(quantity, db_management)
    text_list = await group_list_update_manga(updates, db_management)
    await callback.answer()
    for text in text_list:
        await callback.message.answer(
            text=text,
            reply_markup=update_manga_keyboard
        )


# Для отправки сообщения всем существующим в БД пользователям
@router.message(Text(startswith='/send_message'))
async def process_semd_to_all_live_users(message: Message, bot: Bot, **kwargs):
    db_management = kwargs.get('database_management')
    await bot_send_to_all_user_live(bot, message.text, db_management)


# Для Подсчета живых пользователей
@router.message(Text(text='/stat'))
async def process_send_statistic(message: Message, bot: Bot, **kwargs):
    db_management = kwargs.get('database_management')
    await bot_send_statistic(bot, message.chat.id, db_management)
