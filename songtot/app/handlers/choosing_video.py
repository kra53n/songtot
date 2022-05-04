from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup


class Video(StatesGroup):
    name = State()


async def searching_options(message: types.Message):
    buttons = (
        types.InlineKeyboardButton('search 🔍', callback_data='search'),
        types.InlineKeyboardButton('url 🔗', callback_data='url'),
    )
    kb = types.InlineKeyboardMarkup()
    for button in buttons:
        kb.insert(button)
    await message.answer('Выберите опцию', reply_markup=kb)


def register_searching_method(dp: Dispatcher):
    dp.register_message_handler(searching_options, commands=['search'])


def choosing_video_options(videos_data: list, page: int):
    keycap_symbols = [*map(lambda x: ''.join((f'{d}⃣' for d in str(x))), range(page * 5 + 1, (page + 1) * 5 + 1))]
    buttons = [types.InlineKeyboardButton(f"{keycap_symbols[idx-1]} {vd['title']}", callback_data=f'vd{idx}')
               for idx, vd in enumerate(videos_data, 1)]
    kb = types.InlineKeyboardMarkup()
    for button in buttons:
        kb.add(button)
    kb.add(types.InlineKeyboardButton('⬅ пред', callback_data='vd6'))
    kb.insert(types.InlineKeyboardButton('след ➡️', callback_data='vd7'))
    kb.add(types.InlineKeyboardButton('❌ отмена', callback_data='vd8'))
    return kb
