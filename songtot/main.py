import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from songdl import search_videos_by_query, load_video_to_server
from app.config_reader import load_config
from app.handlers.common_commands import register_start_option
from app.handlers.choosing_video import searching_options, register_searching_method, choosing_video_options


bot = Bot(token=load_config('config/config_example.ini').tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())
messages_to_delete = []


class SearchState(StatesGroup):
    query_name = State()


class SearchOptionState:
    videos_data = None
    page: int = 0


async def give_video_options(message: types.Message):
    page = SearchOptionState.page
    await bot.send_message(
        chat_id=message.chat.id,
        text='Выберите видео',
        reply_markup=choosing_video_options(SearchOptionState.videos_data[page:page+5], page),
    )


@dp.message_handler(state=SearchState.query_name)
async def get_query_name(message: types.Message, state: FSMContext):
    if messages_to_delete:
        msg = messages_to_delete.pop()
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    await state.update_data(query_name=message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    data = await state.get_data()
    SearchOptionState.videos_data = await search_videos_by_query(data['query_name'], 15)
    await state.finish()
    await give_video_options(message)


async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Начать'),
            types.BotCommand('search', 'Искать'),
        ]
    )


async def greeting(id):
    to_print = 'Now Im just an example of message😅'
    await bot.send_message(chat_id=id, text=to_print)


async def process_video_controller_buttons(call: types.CallbackQuery, btn: int):
    if btn == 5 and SearchOptionState.page:
        SearchOptionState.page -= 1
        await give_video_options(call.message)
        await process_video_buttons(call)
    if btn == 6 and SearchOptionState.page != 2:
        SearchOptionState.page += 1
        await give_video_options(call.message)
        await process_video_buttons(call)
    if btn == 7:
        pass


async def process_video_buttons(call: types.CallbackQuery):
    btn = call.data[-1]
    btn = int(btn)-1 if btn.isdigit() else await searching_options(call.message)
    video_data = SearchOptionState.videos_data[btn+SearchOptionState.page]
    if btn in (5, 6, 7):
        await process_video_controller_buttons(call, btn)
        return

    msg = await bot.send_message(chat_id=call.from_user.id, text=f'{video_data["title"]} загружается')
    await load_video_to_server(video_data['href'], video_data['title'])
    await bot.delete_message(chat_id=call.from_user.id, message_id=msg.message_id)

    song_name = video_data['title'] + '.mp3'
    await bot.send_audio(
        call.from_user.id,
        open(song_name, 'rb'),
        caption='Gregory Music Bot',
        title=video_data['title'],
    )
    os.remove(song_name)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('vd'))
async def process_callback_video_option(call: types.CallbackQuery):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except MessageToDeleteNotFound:
        pass
    await process_video_buttons(call)
    await searching_options(call.message)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('search'))
async def process_callback_search(call: types.CallbackQuery):
    messages_to_delete.append(await bot.send_message(call.from_user.id, text='Введите запрос'))
    if call.data == 'search':
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    SearchOptionState.page = 0
    await SearchState.query_name.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('url'))
async def process_callback_url(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id, text='Нажата pressed 😉', show_alert=True)


async def main(dp: Dispatcher):
    await set_commands(bot)

    register_start_option(dp)
    register_searching_method(dp)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main(dp))
