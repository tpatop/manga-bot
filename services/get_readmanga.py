import asyncio
from time import perf_counter

from aiogram import Bot

from database.db_update import read_all_update_status_false, create_update_table, add_update, remake_update_status_in_true
from database.db_users import change_user_live_status, create_user_table, get_users_all_target, remake_list_user_without_all_target
from database.db_description import read_users_by_name_manga
from lexicon.lexicon_ru import group_list_update_manga
from keyboards.keyboards import update_manga_keyboard
from aiogram.exceptions import TelegramForbiddenError


TIME_SLEEP = 600  # 10 минут


async def bot_send(bot: Bot, chat_id: int, text: str):
    try:
        await bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=update_manga_keyboard)
        return True
    except TelegramForbiddenError:  # пользователь заблокировал
        await change_user_live_status(user_id=chat_id)
        return False


# принимает список Update
async def send_message_to_target_users(bot: Bot, updates: list):
    if updates is not None:
        user_update_dict = {}
        for update in updates:
            users = await read_users_by_name_manga(update.name)  # list[int] - пользовательских id
            if users is None:
                continue
            else:
                users = await remake_list_user_without_all_target(users)  # очистка от ошибок, связанных с появлением в списке all_target пользователей
            if users is not None:
                for user_id in users:
                    if user_id not in user_update_dict:
                        user_update_dict[user_id] = [update]
                        continue
                    user_update_dict[user_id].append(update)

        for chat_id, updates in user_update_dict.items():
            text_list = await group_list_update_manga(updates)
            for text in text_list:
                result = await bot_send(bot, chat_id, text)
                # добавляем паузу, чтобы не привысить лимиты Telegram API
                await asyncio.sleep(0.075)
                if not result:
                    break


# функция для отправки сообщения всем пользователям из списка
async def send_message_to_all_target_users(bot: Bot, text_list: list[str]):
    if text_list is not None:
        users = await get_users_all_target()
        if users is not None:
            ignore_user = []  # здесь невозможно остановить пользователя, так как в след тексте он будет
            for text in text_list:
                for user in users:
                    if user in ignore_user:  # если бот заблокирован у бота, то он игнорируется после 1го изменения статуса
                        continue
                    chat_id = int(user.user_id)
                    result = await bot_send(bot, chat_id, text)
                    # добавляем паузу, чтобы не привысить лимиты Telegram API
                    await asyncio.sleep(0.075)  # min = 0.05
                    if not result:
                        ignore_user.append(user)


async def some_coroutine(bot: Bot):
    # start = perf_counter()
    await add_update()
    # print(f'Обработка обновлений заняло = {perf_counter() - start} сек.')

    await asyncio.sleep(5)

    # start = perf_counter()
    updates = await read_all_update_status_false()  # список всех обновлений Update со статусом false
    if updates:
        await send_message_to_target_users(bot, updates)  # рассылка по target
        updates_list = await group_list_update_manga(updates)  # группированный список обновлений в виде объединенных в строку
        await send_message_to_all_target_users(bot, updates_list)  # массовая рассылка all_target
        await remake_update_status_in_true()  # перевод у всех обновлений статуса в true
    # print(f'Рассылка обновлений заняла = {perf_counter() - start} сек.')


async def additional(bot: Bot):
    # start = perf_counter()
    await create_update_table()
    await create_user_table()
    # print(f'Создание БД заняло = {perf_counter() - start} сек.')
    while True:
        try:
            await some_coroutine(bot)
        except Exception as exc:
            print(f'Произошла ошибка:\n{exc}')
        finally:
            await asyncio.sleep(TIME_SLEEP)


# if __name__ == '__main__':
#     bot = Bot(token='6202680256:AAGtrg3Ln5aQsJl-NXu6oVgOt_W2C1TbkFA')
#     asyncio.run(additional())
