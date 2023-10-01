import asyncio
import time

from aiogram import Bot
from database.db_update import (
    read_all_update_status_false,
    add_update,
    remake_update_status_in_true
)
from database.db_users import (
    get_users_live,
    change_user_live_status,
    get_users_all_target,
    remake_list_user_without_all_target
)
from database.db_description import read_users_by_name_manga
from lexicon.lexicon_ru import group_list_update_manga
from keyboards.keyboards import update_manga_keyboard
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database.management import DatabaseManagement


TIME_SLEEP = 300  # 5 минут


async def bot_send(
    bot: Bot, chat_id: int, text: str, db_management: DatabaseManagement
):
    try:
        await bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=update_manga_keyboard)
        return True
    except TelegramForbiddenError:  # пользователь заблокировал
        await change_user_live_status(
            user_id=chat_id, db_management=db_management)
        return False


async def bot_send_to_all_user_live(
    bot: Bot, text: str, db_management: DatabaseManagement
):
    users = await get_users_live(db_management)
    text = text.replace('/send_message ', '')
    for user_id in users:
        try:
            await bot.send_message(
                            chat_id=user_id,
                            text=text)
        except (TelegramForbiddenError, TelegramBadRequest):
            await change_user_live_status(
                user_id=user_id, db_management=db_management)


async def bot_send_statistic(
    bot: Bot, user_id: int, db_management: DatabaseManagement
):
    users = await get_users_live(db_management)
    stat = len(users)
    await bot.send_message(
            chat_id=user_id,
            text=f"{stat} живых пользователей")


# принимает список Update
async def send_message_to_target_users(
    bot: Bot, updates: list, db_management: DatabaseManagement
):
    if updates is not None:
        user_update_dict = {}
        for update in updates:
            # list[int] - пользовательских id
            users = await read_users_by_name_manga(update.name, db_management)
            if users is None:
                continue
            else:
                # очистка от ошибок, связанных с появлением в списке
                # all_target пользователей
                users = await remake_list_user_without_all_target(
                    users, db_management)
            if users is not None:
                for user_id in users:
                    if user_id not in user_update_dict:
                        user_update_dict[user_id] = [update]
                        continue
                    user_update_dict[user_id].append(update)

        for chat_id, updates in user_update_dict.items():
            text_list = await group_list_update_manga(updates, db_management)
            for text in text_list:
                result = await bot_send(bot, chat_id, text, db_management)
                # добавляем паузу, чтобы не привысить лимиты Telegram API
                await asyncio.sleep(0.075)
                if not result:
                    break


# функция для отправки сообщения всем пользователям из списка
async def send_message_to_all_target_users(
    bot: Bot, text_list: list[str], db_management: DatabaseManagement
):
    if text_list is not None:
        users = await get_users_all_target(db_management)
        if users is not None:
            # здесь невозможно остановить пользователя, так как
            # в следующем тексте он будет
            ignore_user = []
            for text in text_list:
                for user_id in users:
                    # если бот заблокирован у бота,
                    # то он игнорируется после 1го изменения статуса
                    if user_id in ignore_user:
                        continue
                    result = await bot_send(bot, user_id, text, db_management)
                    # добавляем паузу, чтобы не привысить лимиты Telegram API
                    await asyncio.sleep(0.075)  # min = 0.05
                    if not result:
                        ignore_user.append(user_id)


async def some_coroutine(
        number_url: int, bot: Bot,
        db_management: DatabaseManagement
):
    await add_update(number_url, db_management)
    updates = await read_all_update_status_false(db_management)
    if updates:
        # рассылка по target
        await send_message_to_target_users(bot, updates, db_management)
        # группированный список обновлений в виде объединенных в строку
        updates_list = await group_list_update_manga(updates, db_management)
        # массовая рассылка по all_target
        await send_message_to_all_target_users(
            bot, updates_list, db_management)
        # перевод у всех обновлений статуса в true
        await remake_update_status_in_true(db_management)


async def additional(bot: Bot, db_management: DatabaseManagement):
    number_url = -1
    while True:
        try:
            number_url = (number_url + 1) % 3
            await some_coroutine(number_url, bot, db_management)
        except Exception as exc:
            print('Произошла ошибка в ',
                  f'{time.strftime("%H.%M.%S", time.localtime())}:',
                  f'\n\t{exc}\n', sep='')
            with open('errors.txt', 'a', encoding='UTF-8') as file:
                print('Произошла ошибка в ',
                      f'{time.strftime("%H.%M.%S", time.localtime())}:',
                      f'\n\t{exc}\n', file=file, sep='')
        finally:
            await asyncio.sleep(TIME_SLEEP)
