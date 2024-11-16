import telebot
from my_secrets import secrets
from telebot import types
import psycopg2
import pandas as pd

token = secrets.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)

# Переменные для отслеживания состояния
awaiting_salary_amount = {}
awaiting_expense_amount = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    query = "SELECT EXISTS (SELECT 1 FROM users WHERE telegram_id = {0});".format(message.chat.id)
    answer = db_query(query)
    if answer[0] == True:
        initialize_main_buttons(message)
    else:
        bot.send_message(
            message.chat.id,
            text="Привет, {0.from_user.first_name}. "
                 "\nВас нет в базе данных зарегистрированных пользователей, обратитсь к администратору"
                 "\nВаш id {0.chat.id}".format(message),
        )


def db_query(query):
    try:
        connection = psycopg2.connect(
            host="localhost",
            dbname=secrets.get('db_name'),
            user=secrets.get('db_user'),
            password=secrets.get('db_password')
        )
        cursor = connection.cursor()
        cursor.execute(query)
        answer = cursor.fetchall()
        result = []
        for i in answer:
            for j in i:
                result.append(j)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"
    finally:
        connection.close()


def db_query_table(query):
    try:
        connection = psycopg2.connect(
            host="localhost",
            dbname=secrets.get('db_name'),
            user=secrets.get('db_user'),
            password=secrets.get('db_password')
        )
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"
    finally:
        connection.close()


def db_transaction(query):
    host = "localhost"
    dbname = secrets.get('db_name')
    user = secrets.get('db_user')
    password = secrets.get('db_password')
    connection = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port="5432"
    )
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                print("Транзакция выполнена успешно!")
                return "Транзакция выполнена успешно!"

    except psycopg2.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return f"Ошибка выполнения запроса: {e}"
    finally:
        connection.close()


def initialize_main_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    result_button = types.KeyboardButton("Итог")
    add_money_button = types.KeyboardButton("Добавить зарплату")
    check_category_button = types.KeyboardButton("Добавить расход")
    name = ""
    if message.from_user.first_name == "Ana":
        name = "❤Настенька❤"
    elif message.from_user.first_name == "Silence":
        name = "Дима🦾"

    markup.add(check_category_button, add_money_button, result_button)
    bot.send_message(
        message.chat.id,
        text="Привет, {0} воспользуйся кнопками".format(name),
        reply_markup=markup
    )


def main_menu(message):
    initialize_main_buttons(message)


def result_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    now_money_button = types.KeyboardButton("Текущие средства")
    sum_expense_button = types.KeyboardButton("Сумма расходов за месяц")
    sum_income_button = types.KeyboardButton("Сумма доходов за месяц")
    table_month_button = types.KeyboardButton("Сводная таблица за месяц")
    table_all_expenses_bytton = types.KeyboardButton("Сводная таблица за всё время")
    main_menu_button = types.KeyboardButton("В главное меню")
    markup.add(now_money_button, sum_expense_button, sum_income_button, table_month_button, table_all_expenses_bytton,
               main_menu_button)
    bot.send_message(
        message.chat.id,
        text="Выберите категорию",
        reply_markup=markup
    )


def add_money_button(message):
    global awaiting_salary_amount
    awaiting_salary_amount[message.chat.id] = True
    bot.send_message(message.chat.id, text="Введите сумму зарплаты:")


def now_money_button(message):
    query = "SELECT SUM(money) FROM users;"
    all_money = db_query(query)
    query = "SELECT ((SELECT SUM(money) FROM expenses WHERE income = true) - (SELECT SUM(money) FROM expenses WHERE income = false)) as dif FROM expenses GROUP BY dif"
    dif = db_query(query)
    all_money = float(all_money[0])
    dif = float(dif[0])
    bot.send_message(
        message.chat.id,
        text="Все средства: {0}\nДоходы - расходы: {1}".format(all_money, dif),
    )


def sum_expense_button(message):
    query = "SELECT SUM(money) FROM expenses WHERE income = false and (SELECT EXTRACT(MONTH FROM date) AS current_month) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE) AS current_month);"
    all_expenses = db_query(query)
    all_expenses = float(all_expenses[0])
    query = "SELECT  SUM(expenses.money) FROM expenses JOIN users ON users.id = expenses.uid WHERE income = false and (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE)) and category_id = 4 and telegram_id = {0};".format(
        message.chat.id)
    my_expenses = db_query(query)
    my_expenses = float(my_expenses[0])
    bot.send_message(
        message.chat.id,
        text="Мои расходы : {1}"
             "\nОбщие расходы : {0}".format(all_expenses, my_expenses),
    )


def sum_income_button(message):
    query = "SELECT SUM(money) FROM expenses WHERE income = true and (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE))"
    all_income = db_query(query)
    all_income = float(all_income[0])
    query = "SELECT  SUM(expenses.money) FROM expenses JOIN users ON users.id = expenses.uid WHERE income = false and (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE)) and telegram_id = {0};".format(
        message.chat.id)
    my_income = db_query(query)
    my_income = float(my_income[0])
    bot.send_message(
        message.chat.id,
        text="Мои доходы : {1}"
             "\nОбщие доходы : {0}".format(all_income, my_income),
    )


def table_month_button(message):
    query = """
    SELECT  
       users.name AS name, 
       categories.name AS category, 
       CASE 
           WHEN expenses.income = FALSE THEN expenses.money * -1
           ELSE expenses.money
       END AS money, 
       expenses.comment
    FROM expenses
    JOIN users ON users.id = expenses.uid
    LEFT JOIN categories ON categories.id = expenses.category_id
    WHERE EXTRACT(MONTH FROM expenses.date) = EXTRACT(MONTH FROM CURRENT_DATE);
    """
    table = db_query_table(query)
    bot.send_message(
        message.chat.id,
        text="Сводная таблица за месяц : \n{0}".format(table)
    )


def table_all_time_button(message):
    query = """
    SELECT  
       users.name AS name, 
       categories.name AS category, 
       CASE 
           WHEN expenses.income = FALSE THEN expenses.money * -1
           ELSE expenses.money
       END AS money, 
       expenses.comment
    FROM expenses
    JOIN users ON users.id = expenses.uid
    LEFT JOIN categories ON categories.id = expenses.category_id;
    """
    table = db_query_table(query)
    bot.send_message(
        message.chat.id,
        text="Сводная таблица за все время : \n{0}".format(table)
    )


def check_category_button(message):
    query = "SELECT name FROM categories;"
    categories = db_query(query)
    category_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons_categories = []
    for name in categories:
        buttons_categories.append(types.KeyboardButton(name))
    for i in buttons_categories:
        category_markup.add(i)
    main_menu_button = types.KeyboardButton("В главное меню")
    category_markup.add(main_menu_button)
    bot.send_message(
        message.chat.id,
        text="Выберите категорию расходов:",
        reply_markup=category_markup
    )


@bot.message_handler(content_types=['text'])
def buttons(message):
    global awaiting_salary_amount, awaiting_expense_amount

    categories = db_query("SELECT name FROM categories;")
    if message.text == "Итог":
        result_button(message)
    elif message.text == "В главное меню":
        main_menu(message)
    elif message.text in categories:
        awaiting_expense_amount[message.chat.id] = message.text
        bot.send_message(message.chat.id, text="Введите сумму расходов для категории и комментарий:")

    elif message.text == "Добавить зарплату":
        add_money_button(message)

    elif message.text == "Добавить расход":
        check_category_button(message)

    elif message.text == "Текущие средства":
        now_money_button(message)
    elif message.text == "Сумма расходов за месяц":
        sum_expense_button(message)
    elif message.text == "Сумма доходов за месяц":
        sum_income_button(message)
    elif message.text == "Сводная таблица за месяц":
        table_month_button(message)
    elif message.text == "Сводная таблица за всё время":
        table_all_time_button(message)
    elif awaiting_salary_amount.get(message.chat.id):
        try:
            text = message.text
            words = text.split()
            money = float(words[0])
            comment = ""
            for word in words[1:]:
                comment += word + " "
            transaction_query = """
                        DO $$
                        DECLARE
                            user_id INT;
                        BEGIN
                            -- Найти ID пользователя по telegram_id
                            SELECT id INTO user_id
                            FROM users
                            WHERE telegram_id = {0};

                            IF user_id IS NULL THEN
                                RAISE EXCEPTION 'Пользователь с telegram_id {0} не найден';
                            END IF;



                            -- Вычесть деньги из баланса пользователя
                            UPDATE users
                            SET money = money + {1}
                            WHERE id = user_id;

                            -- Добавить запись в таблицу expenses
                            INSERT INTO expenses (uid, money, comment, income, date)
                            VALUES (user_id, {1}, '{2}', TRUE, CURRENT_TIMESTAMP);
                        END $$;
                        """.format(message.chat.id, money, comment)
            answer_db = db_transaction(transaction_query)

            bot.send_message(message.chat.id, text=answer_db)
            initialize_main_buttons(message)  # Возвращаем начальные кнопки после выполнения
        except ValueError:
            bot.send_message(message.chat.id, text="Пожалуйста, введите корректное число.")
        awaiting_salary_amount[message.chat.id] = False

    elif awaiting_expense_amount.get(message.chat.id):
        try:
            text = message.text
            words = text.split()
            money = float(words[0])
            comment = ""
            for word in words[1:]:
                comment += word + " "
            category = awaiting_expense_amount[message.chat.id]

            transaction_query = """
            DO $$
            DECLARE
                user_id INT;
                category_id INT;
            BEGIN
                -- Найти ID пользователя по telegram_id
                SELECT id INTO user_id
                FROM users
                WHERE telegram_id = {0};

                IF user_id IS NULL THEN
                    RAISE EXCEPTION 'Пользователь с telegram_id {0} не найден';
                END IF;

                SELECT id INTO category_id
                FROM categories
                WHERE name = '{1}';

                IF category_id IS NULL THEN
                    RAISE EXCEPTION 'Категория с именем {1} не найдена';
                END IF;

                -- Вычесть деньги из баланса пользователя
                UPDATE users
                SET money = money - {2}
                WHERE id = user_id;

                -- Добавить запись в таблицу expenses
                INSERT INTO expenses (uid, category_id, money, comment, income, date)
                VALUES (user_id, category_id, {2}, '{3}', FALSE, CURRENT_TIMESTAMP);
            END $$;
            """.format(message.chat.id, category, money, comment)
            answer_db = db_transaction(transaction_query)

            bot.send_message(message.chat.id, text=answer_db)
            initialize_main_buttons(message)
        except ValueError:
            bot.send_message(message.chat.id, text="Пожалуйста, введите корректное число.")
        awaiting_expense_amount[message.chat.id] = None

    else:
        bot.send_message(message.chat.id, text="Я могу отвечать только на нажатие кнопок.")


bot.polling(none_stop=True, interval=0)
