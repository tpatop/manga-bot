import asyncio

from aiogram import Bot, Dispatcher

from config_data.config import load_config, Config
import handlers.middleware as middleware
from handlers.user_handlers import router as router1
from handlers.other_handlers import router as router2
from services.get_readmanga import additional
from database import DatabaseManagement, init


bot: Bot


async def main():
    # Инициализируем асинхронную сессию к БД
    database_management = DatabaseManagement(await init())
    # Загружаем конфиг в переменную среду
    config: Config = load_config(None)

    # Создание объекта бота и диспетчера
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # регистрируем middleware
    dp.update.middleware(middleware.PassManagementMiddleware(database_management))
    dp.message.middleware(middleware.user_in_database_middleware)

    # регистрация роутеров в диспетчере
    dp.include_router(router1)
    dp.include_router(router2)

    # удаляем предыдущие запросы
    # await bot.delete_webhook(drop_pending_updates=True)
    # # создаем меню
    # await set_main_menu(bot)
    # удаляем меню
    # await bot.delete_my_commands()

    # DataBase - сохранение пользователей
    asyncio.create_task(additional(bot))  # бесконечный цикл
    await dp.start_polling(bot, polling_timeout=30)
    # добавление функции обращения к readmanga


if __name__ == '__main__':

    try:
        # Запускаем функцию main в асинхронном режиме
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
