import sqlite3 as sqlite
from os import system as execute

BDNAME = input("Введите название файла базы данных\n\n>>> ")

# Creating config file

def config(TOKEN, BASENAME):

    execute("cls")
    # # execute("clear")

    open("config.py", 'w').write(
        f"TOKEN = '{TOKEN}'\n" +
        f"BASENAME = '{BASENAME}'"
    )
    print("Config.py создан!")

# Создание базы данных

def base(BASENAME, ADMIN_ID):

    execute("cls")
    # # execute("clear")

    db = sqlite.connect(BASENAME)
    cur = db.cursor()

    try:
        cur.execute(
            """
            CREATE TABLE users (
                id         INTEGER,
                first_name TEXT,
                balance    INTEGER
            );
        """)
        print("Настройка базы данных: 1/7")
    except Exception as e:
        print(f"Не удалось создать таблицу USERS.\n\nПричина: {repr(e)}")

    db.commit()

    try:
        cur.execute(
            """
            CREATE TABLE stats (
                users        INTEGER,
                last_user    INTEGER,
                users_banned INTEGER,
                deps         INTEGER,
                profit       INTEGER,
                buys         INTEGER
            );
        """)
        try:
            cur.execute(
                "INSERT INTO stats VALUES (?,?,?,?,?,?)", (
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                )
            )
        except Exception as e:
            print(repr(e))
        print("Настройка базы данных: 2/7")
    except Exception as e:
        print(f"Не удалось создать таблицу STATS.\n\nПричина: {repr(e)}")

    db.commit()

    try:
        cur.execute(
            """
            CREATE TABLE payment (
                public_key TEXT,
                secret_key TEXT
            );
        """)
        print("Настройка базы данных: 3/7")
    except Exception as e:
        print(f"Не удалось создать таблицу PAYMENT.\n\nПричина: {repr(e)}")

    db.commit()

    try:
        cur.execute(
            """
            CREATE TABLE items (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                cat_id INTEGER,
                name   TEXT,
                about  TEXT,
                price  TEXT,
                data   TEXT
            );
        """)
        print("Настройка базы данных: 4/7")
    except Exception as e:
        print(f"Не удалось создать таблицу PAYMENT.\n\nПричина: {repr(e)}")

    db.commit()

    try:
        cur.execute(
            """
            CREATE TABLE cats (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT,
                aboba INTEGER
            );
        """)
        print("Настройка базы данных: 5/7")
    except Exception as e:
        print(f"Не удалось создать таблицу PAYMENT.\n\nПричина: {repr(e)}")

    db.commit()

    try:
        cur.execute(
            """
            CREATE TABLE bl_id (
                id    INTEGER,
                value INTEGER
            );
        """)
        print("Настройка базы данных: 6/7")
    except Exception as e:
        print(f"Не удалось создать таблицу PAYMENT.\n\nПричина: {repr(e)}")

    db.commit()

    try:
        cur.execute(
            """
            CREATE TABLE admins (
                id       INTEGER,
                username TEXT
            );
        """)
        try:
            cur.execute(
                "INSERT INTO admins VALUES (?,?)", (
                    ADMIN_ID,
                    "ABOBA"
                )
            )

        except Exception as e:
            print(repr(e))
        print("Настройка базы данных: 7/7")
    except Exception as e:
        print(f"Не удалось создать таблицу ADMINS.\n\nПричина: {repr(e)}")

    db.commit()

    if db:
        db.close()

# Установка библиотек

def install_librarys():

    execute("cls")
    # execute("clear")

    execute(
        "pip3 install pyQiwiP2P"
    )
    print("Установка библиотек 1/7")
    execute(
        "pip3 install aiogram"
    )
    print("Установка библиотек 2/7")
    execute(
        "pip3 install uvloop"
    )
    print("Установка библиотек 3/7")
    execute(
        "pip3 install ujson"
    )
    print("Установка библиотек 4/7")
    execute(
        "pip3 install cchardet"
    )
    print("Установка библиотек 5/7")
    execute(
        "pip3 install aiodns"
    )
    print("Установка библиотек 6/7")
    execute(
        "pip3 install aiohttp[speedups]"
    )
    print("Установка библиотек 7/7")
    # print("Установка библиотек 8/8")
    

config(input("Введите токен бота, получить можно тут `@BotFather`\n\n>>>"), BDNAME)
base(BDNAME, input("Введите свой telegram id, получить можно тут `@userinfobot`\n\n>>> "))
install_librarys()