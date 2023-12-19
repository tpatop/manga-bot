from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.lexicon.lexicon_ru import LEXICON_2
from src.keyboards.keyboards import user_menu_keyboard

router = Router()


@router.message(F.text == '/start')
async def process_start_command(message: Message):
    await message.delete()
    text = await LEXICON_2['menu'](message.from_user.id)
    await message.answer(
        text=text,
        reply_markup=user_menu_keyboard
    )
