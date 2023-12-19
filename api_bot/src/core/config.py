from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str              # Токен для доступа к телеграм-боту
#    admin_ids: list[int]   # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN'))
    )
    # ,
    # admin_ids=list(map(int, env.list('ADMIN_IDS')))))
