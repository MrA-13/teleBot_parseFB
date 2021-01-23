from aiogram import Bot, Dispatcher, executor, types 
from aiogram.types import InputMediaPhoto, ParseMode, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Unauthorized
import asyncio
import logging
import datetime
import config
import time
from db import DB_CHENELS
from scrapy import FaceBookBot
import all_plugins


bot_FB = FaceBookBot()
db_chennels = DB_CHENELS()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN_TEST)

storage = MemoryStorage()
dp = Dispatcher(bot, loop=asyncio.get_event_loop(), storage=storage)

# States
class State_admin(StatesGroup):
# Log in in Bot
    logIn = State()
# Add new chennels  
    chennel_id = State()


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    info = """
    Бот працює
    Введіть пароль для авторизації
    """
    await message.answer(info)

"""
ADD NEW CHENNELS
"""

"""
MESSAGES HEDLER
"""

"""
START ADD NEW CHENNEL
- STATE: None -> CHENNEL_ID
- ABOUT: START ADD NEW CHENNEL
"""
@dp.message_handler(state = State_admin.logIn, commands=['add_chennel'])
async def cmd_start_add_new_chennel(message: types.Message, state: FSMContext):
    await state.set_state(State_admin.chennel_id)
    info = """
    Режим додавання нового каналу для постингу постів з ФБ
    ---Для виходу введіть  "/cancel"

Для продовження вставте посилання на телеграм канал
(Наприклад: https://t.me/examplechennel)
    """
    await message.answer(info)

"""
- STATE: CHANNEL'S STATES -> NONE
- ABOUT: EXIT FROM CHANNEL'S STATE
"""
@dp.message_handler(state=State_admin.chennel_id, commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state=State_admin.chennel_id)
async def cancel_handler_chennels_states(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.set_state(State_admin.logIn)
    await message.reply('Ви вийшли з режиму додавання телеграм каналу', reply_markup=types.ReplyKeyboardRemove())

"""
- STATE: CHENNEL_ID -> CHENNEL_ID
- ABOUT: INVALID CONTENT TYPE
"""
@dp.message_handler(lambda message: 'https://t.me/' not in message.text , state=State_admin.chennel_id)
async def invalid_add_new_chennel_handler(message: types.Message, state: FSMContext):
    info = f"""
    Некоректне формат посилання

Для продовження вставте посилання на телеграм канал
(Наприклад: https://t.me/examplechennel)

---Для виходу введіть  "/cancel"
    """
    await message.answer(info)

"""
- STATE: CHENNEL_ID -> CHENNEL_ID
- ABOUT: START ADD NEW CHENNEL
"""
@dp.message_handler(lambda message: 'https://t.me/' in message.text, state=State_admin.chennel_id)
async def cmd_add_chennel_link(message: types.Message, state: FSMContext):

    new_chennel = '@' + message.text.split('https://t.me/')[1]
    db_chennels.add_new_chennel_to_list(new_chennel)
    
    
    await state.set_state(State_admin.logIn)
            
    info = """
    Посилання на канал успішно доданно
Ви вийшли з режиму додавання телеграм каналів

"""
    await message.answer(info) 


"""
LOG IN
"""

"""
MESSAGES HEDLER
"""

"""
START lOG IN
- STATE: NONE -> LOGIN
- ABOUT: RECIEVE PASSWORD
"""
@dp.message_handler()
async def cmd_logIn(message: types.Message, state: FSMContext):
    info_parse_on = """
    Авторизація успішна

/parse_off - включити парсинг
/add_chennel - режим додавання телеграм каналу
/exit - вийти з боту
    """
    info_parse_off = """
    Авторизація успішна

/parse_on - включити парсинг
/add_chennel - режим додавання телеграм каналу
/exit - вийти з боту
    """
    info_False = """
    Пароль невірний, спробуйте ще раз.
    """
    if message.text == config.PASSWORD_TO_BOT:
        await State_admin.logIn.set()
        if config.PARSE_STATE:
            await message.answer(info_parse_on)
        else:
            await message.answer(info_parse_off)
        return
    await message.answer(info_False)

"""
- STATE: LOGIN -> NONE
- ABOUT: RECIEVE EXIT
"""
@dp.message_handler(state = State_admin.logIn, commands = ['exit'])
@dp.message_handler(Text(equals='exit', ignore_case=True), state=State_admin.logIn)
async def cmd_exit(message: types.Message, state: FSMContext):
    await state.finish()
    info = """
    Сеанс закінченно
Для входу введіть пароль
    """
    await message.answer(info)

"""
- STATE: LOGIN -> LOGIN
- ABOUT: PARSE ON
"""
@dp.message_handler(state = State_admin.logIn, commands = ['parse_on'])
@dp.message_handler(Text(equals='parse_on', ignore_case=True), state=State_admin.logIn)
async def cmd_parse_on(message: types.Message):
    config.PARSE_STATE = True
    info = """Парсинг включенно"""
    await message.answer(info)

"""
- STATE: LOGIN -> LOGIN
- ABOUT: PARSE OFF
"""
@dp.message_handler(state = State_admin.logIn, commands = ['parse_off'])
@dp.message_handler(Text(equals='parse_off', ignore_case=True), state=State_admin.logIn)
async def cmd_parse_off(message: types.Message):
    config.PARSE_STATE = False
    info = """Парсинг виключенно"""
    await message.answer(info)


"""
- STATE: LOGIN -> LOGIN
- ABOUT: RECIEVE ANY MESSAGES
"""
@dp.message_handler(state = State_admin.logIn)
async def cmd_any_after_logIn(message: types.Message):
    info_parse_on = """
    /parse_off - включити парсинг
/add_chennel - режим додавання телеграм каналу
/exit - вийти з боту
    """
    info_parse_off = """
    /parse_on - включити парсинг
/add_chennel - режим додавання телеграм каналу
/exit - вийти з боту
    """
    if config.PARSE_STATE:
        await message.answer(info_parse_on)
    else:
        await message.answer(info_parse_off)


async def parse(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        if config.PARSE_STATE:
            posts = bot_FB.get_new_posts()
            for post in posts:
                title_post = post['text'].split('</p>')[0]
                title_post = title_post.split('<p>')[1].split('<br/>')[0]
                text_post = post['text'][len(title_post)+7:]
                if text_post[:3] != "<p>" :
                    text_post = "<p>" + text_post

                post_link = all_plugins.create_telegraph_post(post['photo'], title_post, text_post)
                post_content = f'<a href="{post_link}">{title_post}</a>'
                for chennel_id in db_chennels.chennels:
                    try:
                        await bot.send_message(chennel_id, post_content, parse_mode=ParseMode.HTML, disable_notification=True)
                    except Unauthorized as ex:
                        print(f'Бот не авторизований у цьому каналі - {chennel_id}')


if __name__ == '__main__':
    dp.loop.create_task(parse(config.TIME_FOR_WAIT))
    executor.start_polling(dp, skip_updates=True)
