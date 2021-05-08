import sqlite3 as sqlite # база данных
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery # что бы клаву возвращать
from random import randint # для оплаты и прочего
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime # оплата
import datetime

from config import BASENAME

# ADMIN PANEL START

def admin_panel(user_id):

    if check_admin(user_id) == True:

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Статистика", callback_data="admin > stats"),
            InlineKeyboardButton("Категории & Товары", callback_data="admin > cats and items"),
            InlineKeyboardButton("Платёжные данные", callback_data="admin > payments data"),
            InlineKeyboardButton("В панель участников", callback_data="admin > go to user panel")
        )

        return markup

def avalible_cats():

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute("SELECT * FROM cats")
    except Exception as e:
        print(repr(e))

    x = 0
    cats = []

    while True:

        x += 1
        row = cur.fetchone()

        if row == None:
            break
        if x != 15:
            cats.append(
                f"{row[1]}"
            )

    return cats

def get_cat_id(cat_name):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(f"SELECT * FROM cats WHERE name = '{cat_name}'")
    except Exception as e:
        print(repr(e))

    if not cur.fetchone():

        return 0

    else:

        for i in cur.execute(f"SELECT * FROM cats WHERE name = '{cat_name}'"):

            return i[0]

    if db:
        db.close()

def create_item(cat_name, item_name, item_about, item_price, file_name):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    cat_id = int(get_cat_id(cat_name))

    try:
        cur.executemany("INSERT INTO items (cat_id, name, about, price, data) VALUES (?,?,?,?,?)", [(
            cat_id,
            item_name,
            item_about,
            item_price,
            file_name
        )])

        db.commit()

        return True

    except Exception as e:
        print(repr(e))
        return False

    db.commit()

    if db:
        db.close()

def delete_item(item_id):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(f"DELETE FROM items WHERE id = {item_id}")
        db.commit()
        return "Товар удалён!"
    except Exception as e:
        print(repr(e))
        return "Товар не удалось удалить"

    if db:
        db.close()

def create_category(cat_name):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.executemany("INSERT INTO cats (name, aboba) VALUES (?,?)", [(
            cat_name,
            0
        )])

        db.commit()
        return "Категория успешно создана!"

    except Exception as e:
        print(repr(e))
        return "Категорию не удалось создать"


    if db:
        db.close()

def delete_category(cat_id):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(f"DELETE FROM cats WHERE id = {cat_id}")
        db.commit()
        return True
    except Exception as e:
        print(repr(e))

        return False

    if db:
        db.close()

def admin_stats():

    db = sqlite.connect(BASENAME)
    cur = db.cursor()


    today = datetime.datetime.today().strftime("%Y/%m/%d %H:%m%s")

    try:
        for i in cur.execute(f"SELECT * FROM stats"):

            text = f"| Статистика на {today}\n\nПользователей в боте: {i[0]}\nПоследний пользователь: {i[1]}\n\nПополнений: {i[3]}\nЗаработок от бота: {i[4]} рублей\nПокупок в боте: {i[5]}"
            return text
    except Exception as e:
        print(repr(e))

    if db:
        db.close()

# ADMIN PANEL END

# Добавляем клавиатуру для оплаты

def deposit_markup(amount, user_id, billId):

    markup = InlineKeyboardMarkup(row_width=1) # инициализация клавы

    SECRET_KEY = get_key(1) # запрашиваем приватный ключ

    qapi = QiwiP2P(auth_key=SECRET_KEY) # создаём обработчик 

    bill = qapi.bill(amount=amount, lifetime=10, bill_id=billId)

    link = bill.pay_url # ссылка на оплату

    # Добавляем кнопки в клавиатуру
    markup.add(
        InlineKeyboardButton("Пополнить баланс", url=link),
        InlineKeyboardButton("Проверить пополнение", callback_data=f"check_deposit${billId}")
    )

    # Возвращаем клавиатуру
    return markup

# Проверка оплаты
def check_deposit(billId, user_id):

    # Подключаемся к бд
    db = sqlite.connect(BASENAME) 
    cur = db.cursor()

    # Получаем ключи
    SECRET_KEY = get_key(1)

    # Инициализируем их 
    qapi = QiwiP2P(auth_key=SECRET_KEY)

    # Получаем информацию о платеже с billID
    status = qapi.check(bill_id=billId)

    # Если статус платежа WAITING (ожидание)
    if status.status == "WAITING":
        # Возвращаем False
        return False

    # Если статус платежа PAID (оплачен)
    elif status.status == "PAID":
        try:
            # Анти абуз (т.к при проверке, платежа зачисляет баланс ещё раз :\)
            try:
                cur.execute(f"SELECT * FROM bl_id WHERE id = {billId}")
            except Exception as e:
                print(repr(e))

            if not cur.fetchone():

                # Записываем в переменную X данные о пользователе
                for x in cur.execute(f"SELECT * FROM users WHERE id = {user_id}"):
                    # Получаем сумму из платежа
                    amount = str(status.amount).split(".")
                    # Получаем новый баланс пользователя (баланс пользователя + пополнение (сумма платежа))
                    new_balance = int(x[2]) + int(amount[0])
                    # Обновляем баланс пользователю
                    try:
                        cur.execute(f"UPDATE users SET balance = {new_balance} WHERE id = {user_id}")
                    except Exception as e:
                        print(repr(e))
                    # Сохраняем изменения
                    db.commit()

                    today = datetime.datetime.today().strftime("%Y.%m.%d - %H:%m:%s")

                    print(f"[{today}] > user {user_id} deposit {amount[0]}.")
                # Анти абуз типа    
                try:
                    cur.execute(f"INSERT INTO bl_id VALUES (?,?)", (
                        status.bill_id,
                        status.amount
                    ))
                except Exception as e:
                    print(repr(e))

                db.commit()

                try:
                    for huy in cur.execute(f"SELECT * FROM stats"):

                        new_dep_amount = int(huy[3]) + 1
                        new_profit_amount = int(huy[4]) + float(status.amount)

                        try:
                            cur.execute(
                                f"UPDATE stats SET deps = {new_dep_amount}"
                            )
                            cur.execute(
                                f"UPDATE stats SET profit = {new_profit_amount}"
                            )
                        except Exception as e:
                            print(repr(e))
                except Exception as e:
                    print(repr(e))

                db.commit()
        except Exception as e:
            print(repr(e))

        # Возвращаем True (платёж прошёл)
        return True

    # Закрываем бдшку
    if db:
        db.close()

def get_amount_order(billId):

    # Подключаемся к бд
    db = sqlite.connect(BASENAME) 
    cur = db.cursor()

    # Получаем ключи
    SECRET_KEY = get_key(1)

    # Инициализируем их 
    qapi = QiwiP2P(auth_key=SECRET_KEY)

    # Получаем информацию о платеже с billID
    billInfo = qapi.check(bill_id=billId)

    amount = int(billInfo.amount)

    if db:
        db.close()

    return amount


# Получаем ключи из базы данных для генерации платежа и проверки
def get_key(state):

    # Бд
    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Записываем их в переменную I
    try:
        for i in cur.execute(f"SELECT * FROM payment"):

            # Возвращаем запрошенный ключ (0 - публичный 1 - приватный)
            return str(i[state])

    except Exception as e:
        print(repr(e))

    # Закрываем бдшку

    if db:
        db.close()

# Покупка товара
def buy_item(item_id, user_id):

    # Бд

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Генерация транзакции

    transaction = randint(100000, 999999)

    try:
        # Записываем в переменную I данные о товаре
        for i in cur.execute(f"SELECT * FROM items WHERE id = {item_id}"):
            # Записываем в переменную X данные о пользователе
            for x in cur.execute(f"SELECT * FROM users WHERE id = {user_id}"):
                
                # Проверка баланса
                if int(x[2]) < int(i[4]):

                    return "Не достаточно средств!"

                # Если баланс позволяет купить товар

                elif int(x[2]) >= int(i[4]):

                    # Получаем новый баланс пользователя и сохраняем его

                    try:
                        new_balance = int(x[2]) - int(i[4])

                        cur.execute(f"UPDATE users SET balance = {new_balance} WHERE id = {user_id}")

                    except Exception as e:
                        print(repr(e))
                        return "Попробуйте позже!"

                    try:
                        for aboba in cur.execute("SELECT * FROM stats"):

                            new_buy_amount = int(aboba[5]) + 1

                            try:
                                cur.execute(f"UPDATE stats SET buys = {new_buy_amount}")
                            except Exception as e:
                                print(repr(e))
                    except Exception as e:
                        print(repr(e))

                    db.commit()

                    # Отсылаем сообщение
                    return f"Конфигурация успешно куплена! Номер: {transaction}"
    except Exception as e:
        print(repr(e))   

    if db:
        db.close()

# Отправка файла пользователю
def send_buy(item_id, user_id):

    # Подключаемся к бд

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Получаем название файла и возвращаем его

    try:
        for i in cur.execute(f"SELECT * FROM items WHERE id = {item_id}"):

            return str(i[5])

            today = datetime.datetime.today().strftime("%Y.%m.%d - %H:%m:%s")

            print(f"[{today}] > bot send file {str(i[5])} to {user_id}")

    except Exception as e:
        print(repr(e))

    # Закрываем бд

    if db:
        db.close()       

# Выбор товара

def get_item_about(item_id, user_id):

    # БД

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Получаем информацию о товаре

    try:
        for i in cur.execute(f"SELECT * FROM items WHERE id = {item_id}"):

            # new_balance = int(get)

            text = f"| Покупка '<i>{i[2]}</i>'\n\n" \
                f"О товаре: <i>{i[3]}</i>\n\nЦена: <b>{i[4]}</b> руб.\nВаш баланс после покупки: <b>{int(get_balance(user_id))- int(i[4])} руб.</b>"

    except Exception as e:
        print(repr(e))

    # Возвращаем информацию о товаре

    return text

    # Закрываем бд

    if db:
        db.close()

# Клавиатура покупки товара
def get_item_markup(item_id):

    # БД

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Клава

    markup = InlineKeyboardMarkup(row_width=1)

    # Записываем данные (id) товара в переменную I

    try:
        for i in cur.execute(f"SELECT * FROM items WHERE id = {item_id}"):
            # Добавляем кнопки
            markup.add(
                InlineKeyboardButton("Купить", callback_data=f"buy_item${item_id}"),
                InlineKeyboardButton("Выбрать другой товар", callback_data=f"select_cat${i[1]}")
            )
    except Exception as e:
        print(repr(e))

    return markup

    if db:
        db.close()

# Даём пользователю выбрать товары из выбранной категории

def get_items_in_cat(cat_id):

    # БД

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Получаем список товаров в категории

    try:
        cur.execute(f"SELECT * FROM items WHERE cat_id = {cat_id}")
    except Exception as e:
        print(repr(e))

    # Типа счетчик
    x = 0
    # Клава
    markup = InlineKeyboardMarkup()

    while True:

        # Повышаем счетчик (да да, я спиздил эту технологию с другого скрипта. Но кого это ебет? Всё работает - работает)
        x += 1
        row = cur.fetchone()
    # Дальше полный долбаёб не поймет че за хуйня тут написана
        if row == None:
            break
        if x != 10:
            # Добавляем кнопки
            markup.add(
                InlineKeyboardButton(
                    f"{row[2]} - {row[4]} руб.", callback_data=f"select_item${row[0]}"
                )
            )
    # Ещё одна кнопка блять
    markup.add(
        InlineKeyboardButton(
            "Вернуться", callback_data="go to cat choice"
        )
    )
    # Возвращаем клавиатуру
    return markup

    # Закрываем бд

    if db:
        db.close()

# Даём пользователю выбрать категорию

def get_cats_list():

    # Блять ну это наверное выбор члена

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Получаем категории

    try:
        cur.execute("SELECT * FROM cats")
    except Exception as e:
        print(repr(e))

    # гавно равное нулю
    x = 0 

    # Картошка
    markup = InlineKeyboardMarkup(row_width=1)

    while True:

        x += 1 
        row = cur.fetchone()

        if row == None:
            break
        if x != 10:
            # Лук
            markup.add(
                InlineKeyboardButton(f"{row[1]}", callback_data=f"select_cat${row[0]}")
            )
    # Сутенёр забирает проститутку
    return markup

    # Закрываем пизду твоей мамаше

    if db:
        db.close()

# Выдача баланса

def get_balance(user_id):

    # Олег Монгол

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Получаем лук пользователя по камере

    try:
        for i in cur.execute(f"SELECT * FROM users WHERE id = {user_id}"):

            # Возвращаем оценку его кошелька (0 - нищий 1 - богач)
            return int(i[2])

    except Exception as e:
        print(repr(e))
        return "Попробуйте позже!"

    # Закрываем анус

    if db:
        db.close()

# Проверка на админа (ну тут я забусь писать одно и тоже)

def check_admin(user_id):

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(f"SELECT * FROM admins WHERE id = {user_id}")
    except Exception as e:
        print(repr(e))

    if not cur.fetchone():

        return False

    else:

        return True

    if db:
        db.close()

# Добавление пользователя

def add_user(user_id, first_name, balance, ban):
    # База нахуй
    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    # Получаем инфу о пользователе
    try:
        cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
    except Exception as e:
        print(repr(e))
    # Его нет блять - добавим нахуй
    if not cur.fetchone():
        try:

            cur.execute("INSERT INTO users VALUES (?,?,?,?)", (
                user_id, # Его группа крови
                first_name, # Девечья фамилия матери
                balance, # Состояние после бухича
                ban # Пидорас
            ))

            print(
                "User added!"
            )

        except Exception as e:
            print(repr(e))

        try:
            for x in cur.execute(f"SELECT * FROM stats"):

                new_users_value = int(x[0]) + 1

                try:
                    cur.execute(f"UPDATE stats SET users = {new_users_value}")
                    cur.execute(f"UPDATE stats SET last_user = {user_id}")
                except Exception as e:
                    print(repr(e))

                db.commit()

        except Exception as e:
            print(repr(e))
    # Сохраняем нахуй
    db.commit()

    # Закрываем нахуй
    if db:
        db.close()