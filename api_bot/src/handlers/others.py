import asyncio
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery

from src.lexicon.lexicon_ru import LEXICON, warning_message, TIME_DELETE


router: Router = Router()


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def process_send_bad_answer(message: Message, bot: Bot):
    await message.delete()
    await message.answer(
        text=LEXICON['bad_message_answer'] + warning_message)
    await asyncio.sleep(TIME_DELETE)
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id + 1)


@router.callback_query()  # в каких случаях это возможно? для отладки
async def send_answer_callback(callback: CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback.id,
                                    text=LEXICON['bad_message_answer'],
                                    show_alert=True)
    # await callback.message.answer(text=warning_message + LEXICON['bad_message_answer'])
    # await asyncio.sleep(TIME_DELETE)
    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                          message_id=callback.message.message_id + 1)


# В этом примере мы определили функцию-обработчик process_send_answer,
# которая вызывается при получении сообщения от пользователя.
# Внутри функции мы удаляем полученное сообщение
# (await message.delete()) и отправляем
# пользователю новое сообщение с предупреждением
# (await bot.send_message(message.chat.id, "Внимание!
# Это опасная операция!", parse_mode=types.ParseMode.HTML,
# disable_notification=True)).
# Установка параметра disable_notification в True
#  вызовет отображение уведомления на устройстве пользователя.