import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.core.config import load_config, Config
import src.handlers.middleware as middleware
from src.handlers.users import router as user_router
from src.handlers.others import router as other_router


# Конфигурация логгирования
logging.basicConfig(
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод на консоль
        logging.FileHandler('api_bot/logfile.log')  # Запись в файл
    ],
    level=logging.INFO
)


async def main():
    # Загрузка конфигурации
    config: Config = load_config()

    # Создание объекта бота и диспетчера
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # регистрация middleware
    dp.message.middleware(middleware.user_in_database_middleware)

    # регистрация роутеров в диспетчере
    dp.include_router(user_router)
    dp.include_router(other_router)

    # удаление предыдущих запросов
    # await bot.delete_webhook(drop_pending_updates=True)
    # # создание меню
    # await set_main_menu(bot)
    # удаление меню
    await bot.delete_my_commands()

    # Запуск прослушивания
    await dp.start_polling(bot, polling_timeout=30)


if __name__ == '__main__':

    try:
        # Запускаем функцию main в асинхронном режиме
        # logging.info('Bot start!')
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info('Bot stopped!')
