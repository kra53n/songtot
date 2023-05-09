from aiogram import Dispatcher, types


async def greeting(message: types.Message):
    await message.answer(
        'Добро пожаловать в бота, который скачивает музыку из Ютуба.'
        '\n\nВведите /search, чтобы начать поиск.'
    )


def register_start_option(dp: Dispatcher):
    dp.register_message_handler(greeting, commands=['start'])
