from aiogram import Dispatcher, types


async def greeting(message: types.Message):
    to_print = 'Добро пожаловать в бота, который скачивает музыку из Ютуба.' + \
               '\n\nВведите /search, чтобы начать поиск.'
    await message.answer(to_print)


def register_start_option(dp: Dispatcher):
    dp.register_message_handler(greeting, commands=['start'])
