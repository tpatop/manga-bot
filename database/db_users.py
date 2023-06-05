from services.parser import process_manga_add_parsing
from database.db_description import (
    read_manga_in_target_name,
    del_user_in_manga_decr_db,
    check_manga_in_db, add_description,
    add_user_in_manga_decr_db
)
from services.hash_all import hash_full_text
from .management import DatabaseManagement, UserRepo
from .models import User


async def _get_user(
    user_id: int, db_management: DatabaseManagement
):
    user_id = int(user_id)
    user_repo: UserRepo = db_management.get_user_repo()
    user: User = await user_repo.get_user(user_id)
    return user


async def _update_user(
    user: User, db_management: DatabaseManagement
):
    user_repo: UserRepo = db_management.get_user_repo()
    await user_repo.update_user(user)


async def change_user_all_target(
    user_id: int, db_management: DatabaseManagement
):
    user: User = await _get_user(user_id, db_management)
    user.all_target = not user.all_target
    await _update_user(user, db_management)


async def change_user_live_status(
    user_id: int, db_management: DatabaseManagement
):
    user: User = await _get_user(user_id, db_management)
    user.live_status = not user.live_status
    await _update_user(user, db_management)


async def remake_list_user_without_all_target(
        users: list[int], db_management: DatabaseManagement
) -> list[int]:
    user_repo: UserRepo = db_management.get_user_repo()
    users_list = []
    change_dict = {'all_target': False, 'live_status': True}
    for user_id in users:
        change_dict['user_id'] = user_id
        user = await user_repo.get_users_list(change_dict)
        if user:
            users_list.append(user[0].user_id)
    if users_list is not None and users_list != []:
        return users_list
    return None


async def get_users_all_target(
    db_management: DatabaseManagement
) -> list[int]:
    user_repo: UserRepo = db_management.get_user_repo()
    change_dict = {'all_target': True, 'live_status': True}
    users = await user_repo.get_users_list(change_dict)
    return [user.user_id for user in users]


async def add_manga_in_user_db(
        name: str, user_id: int, db_management: DatabaseManagement
):
    user: User = await _get_user(user_id, db_management)
    if user is not None:
        hash_name = await hash_full_text(name)
        if user.target is None:
            user.target = hash_name
        elif hash_name not in user.target:
            user.target += f' * {hash_name}'
    await _update_user(user, db_management)


async def add_manga_in_target(
    name: str, user_id: int, db_management: DatabaseManagement
):
    await add_user_in_manga_decr_db(name, user_id, db_management)
    await add_manga_in_user_db(name, user_id, db_management)


async def add_manga_in_target_with_url(
        url: str, user_id: int, db_management: DatabaseManagement
):
    update = await process_manga_add_parsing(url)
    if update is not None:
        # name, image_orig_link, manga_genre, manga_description, manga_link
        name = update[0]
        manga_in_db = await check_manga_in_db(name, db_management)
        if not manga_in_db:  # добавляю в БД мангу
            await add_description([update], db_management)
        await add_manga_in_target(name, user_id, db_management)
        return True
    else:
        return False


# переместить данную функцию в description
async def read_manga_in_target(
    user_id: int, db_management: DatabaseManagement
) -> str:
    user: User = await _get_user(user_id, db_management)
    manga_names_link_list = await read_manga_in_target_name(
        user.target, db_management)
    if manga_names_link_list:
        return manga_names_link_list


async def delete_manga_from_target(
    hash_name: str, user_id: id, db_management: DatabaseManagement
):
    if 'del*' in hash_name:
        hash_name = hash_name.replace('del*', '')
    user_repo: UserRepo = db_management.get_user_repo()
    user: User = await user_repo.get_user(user_id)
    if user is not None:
        if user.target is not None:
            if hash_name in user.target:
                manga_list = user.target.split(' * ')
                manga_list = [x for x in manga_list if x != hash_name]
                if manga_list not in ([''], []):
                    user.target = ' * '.join(manga_list)
                else:
                    user.target = None
    await user_repo.update_user(user)
    await del_user_in_manga_decr_db(hash_name, user_id, db_management)


async def check_manga_in_user_target(
        user_id: int, hash_name: str, db_management: DatabaseManagement
) -> bool:
    user: User = await _get_user(user_id, db_management)
    return (False, True)[user.target is not None and hash_name in user.target]
