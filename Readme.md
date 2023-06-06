Test of mirror for gitlab <---> github

На данный момент переделано:
    1. Добавлены миграции к БД с помощью alembic
    2. Перенесено на асинхронный движок модули db_users, db_description, db_update
    3. Добавлен ещё один уровень абстракции к БД