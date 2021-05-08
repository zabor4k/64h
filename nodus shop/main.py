from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot import api
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import sqlite3 as sqlite
from datetime import *
import os
import time
from random import *
from config import TOKEN, BASENAME
import handler

logo = """
          ,-.,-.          
____.___  |(||(| ____.___ 
`----===' (_)(_) `----==='
 ___.____ | || |  ___.____
`===----' | || | `===----'
          `-'`-'          
                          
"""

class dep(StatesGroup):

    amount = State()

class qiwi_tokens(StatesGroup):

    public_key = State()
    secret_key = State()

class add_cat(StatesGroup):

    name = State()

class add_item(StatesGroup):

    cat = State()
    name = State()
    about = State()
    price = State()
    file_name = State()

bot = Bot(token=TOKEN, parse_mode='html')
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)

@dp.message_handler(commands=['start'])
async def start(message):

    handler.add_user(message.from_user.id, message.from_user.first_name, 0, 0)

    if handler.check_admin(message.from_user.id) == False:

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
            KeyboardButton("Товары")
        )

        markup.add(
            KeyboardButton("Банк"),
            
        )

        await message.answer(
            "Привет!", reply_markup=markup
        )

    else:

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("В админ панель", callback_data="admin > admin panel"),
            InlineKeyboardButton("В панель участников", callback_data="admin > go to user panel")
        )

        await message.answer(
            "Привет господин!", reply_markup=markup
        )

@dp.message_handler(content_types=['text'])
async def texts(message):

    if message.chat.type == 'private':

        if "товары" in message.text.lower():

            await message.answer("Выбери категорию", reply_markup=handler.get_cats_list())
        
        elif "пополнить баланс" in message.text.lower():

            await message.answer(
                f"Введите сумму пополнения\n\nМинмальная сумма пополнения: <i>100 рублей</i>\nМаксимальная сумма пополнения: <i>5000 рублей</i>"
            )
            await dep.amount.set()
        
        elif "банк" in message.text.lower():

            markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                KeyboardButton("Пополнить баланс"),
                KeyboardButton("В главное меню")
            )

            await message.answer(
                f"💰 Ваш баланс: <i>{handler.get_balance(message.from_user.id)}</i> руб.", reply_markup=markup
            )

        elif "в главное меню" in message.text.lower():

            markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                KeyboardButton("Товары")
            )

            markup.add(
                KeyboardButton("Банк"),
                
            )

            await message.answer(
                "Привет!", reply_markup=markup
            )

@dp.message_handler(commands=['ahelp'])
async def ahelp(message):

    if handler.check_admin(message.from_user.id) == True:

        ahelp_msg = "| Комманды администратора\n\n" \
            "<b>/mail *message*</b> - отправить сообщение всем пользователям\n<b>/ac *message*</b> - отправить сообщение в чат администраторов"

        await message.answer(
            ahelp_msg
        )

@dp.message_handler(commands=['mail'])
async def admin_mail(message):

    if handler.check_admin(message.from_user.id) == True:

        if message.text.lower() == '/mail' or message.text.lower() == "/mail ":

            await message.answer(
                "Введите комманду /ahelp для того, что бы посмотреть доступные аргументы для комманды /mail"
            )

        else:

            data = str(message.text.lower()).split("/mail ")
            msg = str(data[1])

            db = sqlite.connect(BASENAME)
            cur = db.cursor()

            try:
                for i in cur.execute("SELECT * FROM users"):
                    await bot.send_message(int(i[0]), msg)
            except Exception as e:
                print(repr(e))

            if db:
                db.close()

@dp.message_handler(commands=['ac'])
async def admin_chat(message):

    if handler.check_admin(message.from_user.id) == True:

        if message.text.lower() == '/ac' or message.text.lower() == "/ac ":

            await message.answer(
                "Введите комманду /ahelp для того, что бы посмотреть доступные аргументы для комманды /ac"
            )

        else:

            data = str(message.text.lower()).split("/ac ")
            msg = str(data[1])

            db = sqlite.connect(BASENAME)
            cur = db.cursor()

            try:
                for i in cur.execute("SELECT * FROM admins"):
                    await bot.send_message(int(i[0]), f"[ADMIN CHAT] > {msg}")
            except Exception as e:
                print(repr(e))

            if db:
                db.close()


@dp.message_handler(state=dep.amount, content_types=types.ContentTypes.TEXT)
async def dep_money(message: types.Message, state: FSMContext):

    try:
        if int(message.text) < 1 or int(message.text) > 5000:

            await message.answer(
                "Минмальная сумма пополнения: <i>100 рублей</i>\nМаксимальная сумма пополнения: <i>5000 рублей</i>"
            )
            return
    except Exception as e:
        print(repr(e))

    text = f"Пополнение счета <i>{message.from_user.id}</i> на сумму: <i>{message.text}</i> рублей\n\n"
    text += f"Счет действиетелен в течении 10 минут!"

    mk = handler.deposit_markup(int(message.text), message.from_user.id, randint(100000, 999999))

    await message.answer(text, reply_markup=mk)

    await state.finish()
    
@dp.message_handler(state=qiwi_tokens.public_key, content_types=types.ContentTypes.TEXT)
async def change_qiwi_tokens_step1(message: types.Message, state: FSMContext):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(f"UPDATE payment SET public_key = '{message.text}'")
    except Exception as e:
        print(repr(e))

    db.commit()

    await message.answer(
        "Введите SECRET key"
    )

    # await qiwi_tokens.secret_key.set()
    await qiwi_tokens.next()

    if db:
        db.close()

@dp.message_handler(state=qiwi_tokens.secret_key, content_types=types.ContentTypes.TEXT)
async def change_qiwi_tokens_step2(message: types.Message, state: FSMContext):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(f"UPDATE payment SET secret_key = '{message.text}'")
    except Exception as e:
        print(repr(e))

    db.commit()

    await message.answer(
        "Токены обновлены!"
    )

    await state.finish()

    if db:
        db.close()

@dp.message_handler(state=add_cat.name, content_types=types.ContentTypes.TEXT)
async def add_cat_name(message: types.Message, state: FSMContext):

    await message.answer(
        handler.create_category(message.text)
    )

    await state.finish()

@dp.message_handler(state=add_item.cat, content_types=types.ContentTypes.TEXT)
async def add_item_cat(message: types.Message, state: FSMContext):

    if message.text not in handler.avalible_cats():

        await message.answer("Выбери категорию используя клавиатуру")
        return

    await state.update_data(cat=message.text)
    await add_item.next()
    await message.answer("Добавьте название товару")

@dp.message_handler(state=add_item.name, content_types=types.ContentTypes.TEXT)
async def add_item_name(message: types.Message, state: FSMContext):

    await state.update_data(name=message.text.lower())
    await add_item.next()
    await message.answer("Добавьте описание товару. Есть поддежрка HTML")

@dp.message_handler(state=add_item.about, content_types=types.ContentTypes.TEXT)
async def add_item_about(message: types.Message, state: FSMContext):

    if len(message.text.lower()) < 15:
        await message.answer("Опишите более подбронее")
        return

    await state.update_data(about=message.text.lower())
    await add_item.next()
    await message.answer("Добавьте цену товару")

@dp.message_handler(state=add_item.price, content_types=types.ContentTypes.TEXT)
async def add_item_price(message: types.Message, state: FSMContext):

    try:
        if int(message.text) < 1:
            await message.answer("Товар не может стоить меньше 1 рубля!")
            return 
    except:
        await message.answer("Введите число!")
        return

    await state.update_data(price=int(message.text))
    await add_item.next()
    await message.answer("Введите название файла в котором содержится товар (указывать с расширением .txt/.rar/.zip и т.д")

@dp.message_handler(state=add_item.file_name, content_types=types.ContentTypes.TEXT)
async def add_item_filename(message: types.Message, state: FSMContext):

    data = await state.get_data()

    cat_name = str(data['cat'])
    name = str(data['name'])
    about = str(data['about'])
    price = int(data['price'])
    file_name = str(message.text)

    if handler.create_item(cat_name, name, about, price, file_name) == True:

        await message.answer(
            "Товар успешно создана!"
        )

    else:

        await message.answer(
            "Не удалось создать товар!"
        )

    await state.finish()


@dp.callback_query_handler()
async def call(call):

    # Admin panel call.data

    if call.data == "admin > go to user panel":

        await bot.delete_message(call.message.chat.id, call.message.message_id)

        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(
            KeyboardButton("Товары")
        )

        markup.add(
            KeyboardButton("Банк"),
            
        )

        await bot.send_message(
            chat_id=call.message.chat.id,
            text="Привет!", reply_markup=markup
        )
    
    elif call.data == "admin > admin panel":

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Админ панель",
            reply_markup=handler.admin_panel(call.from_user.id)
        )
    
    elif call.data == "admin > cats and items":

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Управление категориями", callback_data="admin > cats and items > manage cats"),
            InlineKeyboardButton("Управление товарами", callback_data="admin > cats and items > manage items"),
            InlineKeyboardButton("Назад", callback_data="admin > admin panel")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Категории и товары",
            reply_markup=markup
        )

    elif call.data == "admin > cats and items > manage items":

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Добавить товар", callback_data="admin > cats and items > manage items > add item"),
            InlineKeyboardButton("Удалить товар", callback_data="admin > cats and items > manage items > delete item"),
            InlineKeyboardButton("Назад", callback_data="admin > cats and items")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Товары",
            reply_markup=markup
        )

    elif call.data == "admin > cats and items > manage items > add item":

        markup = ReplyKeyboardMarkup(row_width=2)
        for name in handler.avalible_cats():
            markup.add(
                name
            )

        await bot.send_message(
            call.message.chat.id,
            "Выбери категорию", reply_markup=markup
        )
        await add_item.cat.set()
        
    
    elif call.data == "admin > cats and items > manage items > delete item":

        db = sqlite.connect(BASENAME)
        cur = db.cursor()

        try:
            cur.execute(f"SELECT * FROM cats")
        except Exception as e:
            print(repr(e))

        x = 0
        markup = InlineKeyboardMarkup(row_width=1)

        while True:

            x += 1
            row = cur.fetchone()

            if row == None:
                break
            if x != 15:
                markup.add(
                    InlineKeyboardButton(
                        f"Категория : '{row[1]}'", callback_data=f"delete_item1${row[0]}"
                    )
                )

        markup.add(
            InlineKeyboardButton("Назад", callback_data="admin > cats and items > manage items")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Выбери категорию в которой хочешь удалить товар",
            reply_markup=markup
        )

    elif "delete_item1" in call.data:

        db = sqlite.connect(BASENAME)
        cur = db.cursor()

        data = str(call.data).split("$")
        cat_id = int(data[1])

        try:
            cur.execute(f"SELECT * FROM items WHERE cat_id = {cat_id}")
        except Exception as e:
            print(repr(e))

        x = 0
        markup = InlineKeyboardMarkup(row_width=1)

        while True:

            x += 1
            row = cur.fetchone()
            if row == None:
                break
            if x != 10:

                markup.add(
                    InlineKeyboardButton(
                        f"{row[2]} - {row[4]} руб.", callback_data=f"delete_item2${row[0]}"
                    )
                )

        markup.add(
            InlineKeyboardButton(
                f"Назад", callback_data="admin > cats and items > manage items > delete item"
            )
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Выбери товар который хочешь удалить",
            reply_markup=markup
        )

    elif "delete_item2" in call.data:

        data = str(call.data).split("$")
        item_id = int(data[1])

        await call.answer(
            handler.delete_item(item_id)
        )

    elif call.data == "admin > cats and items > manage cats":

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Добавить категорию", callback_data="admin > cats and items > manage cats > add cat"),
            InlineKeyboardButton("Удалить категорию", callback_data="admin > cats and items > manage cats > delete cat"),
            InlineKeyboardButton("Назад", callback_data="admin > cats and items")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Категории",
            reply_markup=markup
        )

    elif call.data == "admin > cats and items > manage cats > add cat":

        await call.answer(
            "Введите название категории\n\nНапример: <i>Skeet</i> или <i>Инвайты</i>"
        )

        await add_cat.name.set()
    
    elif call.data == "admin > cats and items > manage cats > delete cat":

        db = sqlite.connect(BASENAME)
        cur = db.cursor()

        try:
            cur.execute(f"SELECT * FROM cats")
        except Exception as e:
            print(repr(e))

        x = 0
        markup = InlineKeyboardMarkup(row_width=1)

        while True:

            x += 1
            row = cur.fetchone()

            if row == None:
                break
            if x != 15:
                markup.add(
                    InlineKeyboardButton(
                        f"Категория : '{row[1]}'", callback_data=f"delete_cat${row[0]}"
                    )
                )

        markup.add(
            InlineKeyboardButton("Назад", callback_data="admin > cats and items > manage cats")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Выбери категории которые хочешь удалить",
            reply_markup=markup
        )

    elif "delete_cat" in call.data:

        data = str(call.data).split("$")
        cat_id = int(data[1])

        if handler.delete_category(cat_id) == True:

            await call.answer(
                "Категория удалена!"
            )

        else:

            await call.answer(
                "Не удалось удалить категорию!"
            )
    
    elif call.data == "admin > payments data":

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Сменить токены", callback_data="admin > payments data > change tokens"),
            InlineKeyboardButton("Назад", callback_data="admin > admin panel")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Получить токены можно <a href='https://p2p.qiwi.com'>тут</a>",
            reply_markup=markup
        )

    
    elif call.data == "admin > payments data > change tokens":

        await call.answer(
            "Введите PUBLIC key"
        )

        await qiwi_tokens.public_key.set()
    
    elif call.data == "admin > stats":

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Назад", callback_data="admin > admin panel")
        )

        await bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=handler.admin_stats(),
            reply_markup=markup
        )

    # Admin panel call.data
    
    if "check_deposit" in call.data:

        db = sqlite.connect(BASENAME)
        cur = db.cursor()

        data = str(call.data).split("$")
        deposit_id = str(data[1])

        if handler.check_deposit(deposit_id, call.from_user.id) == True:

            await call.answer(
                f"💰 Ваш баланс: {handler.get_balance(call.from_user.id)}"
            )

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                    text="✅ Благодарим вас за пополнение баланса.")

        else:

            await call.answer(
                "❗️ Ваш платёж не был найден."
            )

        try:
            for x in cur.execute(f"SELECT * FROM admins"):

                await bot.send_message(
                    int(x[0]), 
                    f"💰 Пользователь `{call.from_user.id}` пополнил баланс на сумму `{handler.get_amount_order(deposit_id)} руб.`"
                )
        except Exception as e:
            print(repr(e))
    
    elif "buy_item" in call.data:

        data = str(call.data).split("$")
        item_id = int(data[1])

        await bot.send_message(call.message.chat.id,
            handler.buy_item(item_id, call.from_user.id)
        )

        await call.answer(
            f"💰 Ваш баланс: {handler.get_balance(call.from_user.id)}"
        )

        await bot.send_document(
            call.message.chat.id, open(f"aboba/{handler.send_buy(item_id, call.from_user.id)}", 'rb')
        )
    
    elif "select_item" in call.data:

        data = str(call.data).split("$")
        item_id = int(data[1])

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=handler.get_item_about(item_id, call.from_user.id),
            reply_markup=handler.get_item_markup(item_id)
        )
    
    elif call.data == "go to cat choice":

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выбери категории",
            reply_markup=handler.get_cats_list()
        )
    
    elif "select_cat" in call.data:

        data = str(call.data).split("$")

        cat_id = int(data[1])

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выбери товар",
            reply_markup=handler.get_items_in_cat(cat_id)
        )

if __name__ == "__main__":

    print(logo)

    executor.start_polling(dp, skip_updates=True)