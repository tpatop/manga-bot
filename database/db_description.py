from typing import Union
from services.hash_all import hash_full_text
from .management import DatabaseManagement, DescriptionRepo
from .models import Description


async def _get_description(hash_name: str, db_management: DatabaseManagement):
    descr_repo: DescriptionRepo = db_management.get_description_repo()
    result = await descr_repo.get_description(hash_name)
    return result


async def _update_description(
    descr: Description, db_management: DatabaseManagement
):
    descr_repo: DescriptionRepo = db_management.get_description_repo()
    await descr_repo.update_user_in_description(descr)


async def add_description(
        updates: list[tuple[str]], db_management: DatabaseManagement
):
    descr_repo: DescriptionRepo = db_management.get_description_repo()
    try:
        for update in updates:
            name = update[0]
            hash_name = await hash_full_text(name)
            new_description = {
                'name': name,
                'hash_name': hash_name,
                'image': update[2],
                'genre': ', '.join(update[3]),
                'description': update[4],
                'link': update[5]
            }
            # проверка на наличие в таблице
            result = await _get_description(hash_name, db_management)
            if result:
                continue
            else:
                await descr_repo.create_description(new_description)
    except Exception as exc:
        # изменить на запись в файл с указанием времени
        print(f'\t\tПроизошла ошибка в add_description:\n{exc}')
        raise


async def check_manga_in_db(
    name: str, db_management: DatabaseManagement
) -> bool:
    hash_name = await hash_full_text(name)
    result = await _get_description(hash_name, db_management)
    return result is not None


async def add_user_in_manga_decr_db(
        name: str, user_id: int, db_management: DatabaseManagement
):
    hash_name = await hash_full_text(name)
    descr = await _get_description(hash_name, db_management)
    if descr is not None:
        if descr.users is None:
            descr.users = str(user_id)
        elif str(user_id) not in descr.users:  # проверка на пустоту атрибута
            descr.users += f' * {user_id}'
    await _update_description(descr, db_management)


async def del_user_in_manga_decr_db(
    hash_name: str, user_id: int, db_management: DatabaseManagement
):
    descr: Description = await _get_description(hash_name, db_management)
    if descr is not None:
        # проверка на пустоту атрибута
        if descr.users is not None and str(user_id) in descr.users:
            user_list = descr.users.split(' * ')
            user_list = [x for x in user_list if x != str(user_id)]
            if user_list != [''] and user_list != []:
                descr.users = ' * '.join(user_list)
            else:
                descr.users = None
        await _update_description(descr, db_management)


async def read_manga_in_target_name(
        hash_names: str, db_management: DatabaseManagement
) -> list:
    '''Функция для чтения названия манги по списку target пользователя'''
    if hash_names is not None:
        hash_names = hash_names.split(' * ')
        names_link_list = []
        for hash_name in hash_names:
            descr: Description = await _get_description(
                hash_name, db_management)
            if descr is not None:
                name = descr.name
                link = descr.link
                names_link_list.append((name, link))
        return names_link_list


async def read_users_by_name_manga(
    name: str, db_management: DatabaseManagement
) -> Union[list[int], None]:
    hash_name = await hash_full_text(name)
    descr: Description = await _get_description(hash_name, db_management)
    if descr is not None:
        if descr.users is not None:
            users = list(map(int, descr.users.split(' * ')))
            return users
