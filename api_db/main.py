import uvicorn
import logging
from fastapi import FastAPI

from src.api.endpoints.manga import router as manga_router


# Конфигурация логгирования
logging.basicConfig(
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод на консоль
        logging.FileHandler('logfile.log')  # Запись в файл
    ],
    level=logging.INFO
)


app = FastAPI()

app.include_router(prefix='/manga', router=manga_router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0',
                port=8080, reload=True, workers=1)
