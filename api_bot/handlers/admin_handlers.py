# @router.message(Command(commands=['database']))
# async def process_read_database(message: Message):

#     database_name = message.text.split()[1] if len(message.text.split()) > 1 else 'users'
#     await message.delete()
#     if database_name == 'product':
#         await read_product_database()
#     elif database_name == 'users':
#         await read_all_database(message)
#     else:
#         print('Not found!')