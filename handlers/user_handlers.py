import asyncio
from aiogram import Router, Bot
from aiogram.filters import Text, CommandStart
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import group_list_update_manga, create_text_review_manga, warning_message, TIME_DELETE, LEXICON, user_menu_text, text_manga_target
from keyboards.keyboards import update_manga_keyboard, last_update_review_kb, manga_settings_kb, manga_review_kb, create_review_manga_kb, delete_manga_keyboard, user_read_manga_keyboard, start_keyboard, help_keyboard, user_menu_keyboard
from database.db_users import change_user_live_status, change_user_all_target, add_manga_in_target, add_manga_in_target_with_url, delete_manga_from_target
from database.db_update import process_show_desc_updates_list


router: Router = Router()


# Приветствие и открытие начальной страницы /start
@router.message(CommandStart())
async def process_start_command(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
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
async def process_help_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['/help'],
        reply_markup=help_keyboard
    )


@router.callback_query(Text(text='/user_menu'))
async def process_user_menu_start(callback: CallbackQuery):
    await callback.message.edit_text(
        text=await user_menu_text(callback.from_user.id),
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
@router.message(Text(startswith='https://readmanga.live/'))
async def process_add_manga_in_target(message: Message, bot: Bot):
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    result = await add_manga_in_target_with_url(message.text, message.from_user.id)
    await message.delete()
    if result:
        await message.answer(
            text=warning_message + LEXICON['successful_add']
        )
        await asyncio.sleep(TIME_DELETE)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
    else:
        await message.answer(
            text=warning_message + '''Произошла ошибка при добавлении!
            Возможно, Вы ввели неправильный адрес манги!'''
        )
        await asyncio.sleep(TIME_DELETE)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)


@router.callback_query(Text(text='/manga_target'))
async def process_answer_target_manga_for_user(callback: CallbackQuery, bot: Bot):
    text = await text_manga_target(callback.from_user.id)
    await callback.message.edit_text(
        text=text,
        reply_markup=user_read_manga_keyboard)


@router.callback_query(Text(text='/manga_delete'))
async def process_show_manga_in_target_page(callback: CallbackQuery):
    kb = await delete_manga_keyboard(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON['delete_manga_page'],
        reply_markup=kb
    )


@router.callback_query(Text(startswith='del*'))
async def process_delete_manga_from_target(callback: CallbackQuery):
    await delete_manga_from_target(callback.data, callback.from_user.id)
    kb = await delete_manga_keyboard(callback.from_user.id)
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


# обработка нажатия на клавиатуру с названием
@router.callback_query(Text(startswith='rev*'))
async def process_show_review_manga(callback: CallbackQuery):
    hash_name = callback.data[4:]
    text, photo = await create_text_review_manga(hash_name, callback.from_user.id)
    kb = await manga_review_kb(callback.from_user.id, hash_name)
    await callback.message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=kb,
        parse_mode='html'
    )
    await callback.answer()


from services.hash_all import hash_full_text

# добавление в отслеживаемые с помощью инлайн-клавиатуры
@router.callback_query(Text(text='/add_manga_in_target'))
async def process_add_manga_in_target_callback(callback: CallbackQuery, bot: Bot):
    name = callback.message.caption
    name = name[: name.find('[')].strip()  # получил название
    hash_name = await hash_full_text(name)
    await add_manga_in_target(name, callback.message.chat.id)
    await bot.answer_callback_query(callback.id,
                                    text=LEXICON['successful_add'],
                                    show_alert=False)
    text, _ = await create_text_review_manga(hash_name, callback.from_user.id)
    await callback.message.edit_caption(
        caption=text,
        reply_markup=await manga_review_kb(callback.from_user.id, hash_name)
    )


# обратное действие (удаление из списка)
@router.callback_query(Text(text='/del_manga_in_target'))
async def process_del_manga_in_target_callback(callback: CallbackQuery, bot: Bot):
    name = callback.message.caption
    name = name[: name.find('[')].strip()  # получил название
    hash_name = await hash_full_text(name)
    await delete_manga_from_target(await hash_full_text(name), callback.message.chat.id)
    await bot.answer_callback_query(callback.id,
                                    text=LEXICON['successful_del'],
                                    show_alert=False)
    text, _ = await create_text_review_manga(hash_name, callback.from_user.id)
    await callback.message.edit_caption(
        caption=text,
        reply_markup=await manga_review_kb(callback.from_user.id, hash_name)
    )


@router.callback_query(Text(text='/settings'))
async def show_settings_for_user(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['settings_menu'],
        reply_markup=await manga_settings_kb(callback.from_user.id)
    )

    # '/all_target_false': 'Обновления из списка',
    # '/all_target_true': 'Все обновления сайта',
    # '/status_live_true': 'Не получать обновления!',
    # '/status_live_false': 'Получать обновления!'


@router.callback_query(Text(text='/all_target_true'))
@router.callback_query(Text(text='/all_target_false'))
async def process_all_target_user_change(callback: CallbackQuery):
    await change_user_all_target(callback.from_user.id)
    await callback.message.edit_reply_markup(
        text=LEXICON['settings_menu'],
        reply_markup=await manga_settings_kb(callback.from_user.id)
    )


@router.callback_query(Text(text='/status_live_true'))
@router.callback_query(Text(text='/status_live_false'))
async def process_user_status_live_change(callback: CallbackQuery):
    await change_user_live_status(callback.from_user.id)
    await callback.message.edit_reply_markup(
        text=LEXICON['settings_menu'],
        reply_markup=await manga_settings_kb(callback.from_user.id)
    )


@router.callback_query(Text(text='/show_update'))
async def process_show_menu_update_viewer(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['show_update'],
        reply_markup=last_update_review_kb
    )
    

@router.callback_query(Text(startswith='/showup*'))
async def process_show_update_viewer(callback: CallbackQuery):
    quantity = int(callback.data.split()[1])
    updates = await process_show_desc_updates_list(quantity)
    text_list = await group_list_update_manga(updates)
    await callback.answer()
    for text in text_list:
        await callback.message.answer(
            text=text,
            reply_markup=update_manga_keyboard
        )
