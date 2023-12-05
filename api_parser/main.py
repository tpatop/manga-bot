'''
TODO:
1. Качать данные со страницы
2. Парсить данные
3. Добавлять данные в БД
'''

import uvicorn
from fastapi import APIRouter


app = APIRouter()


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0',
                port=8080, reload=True, workers=1)
