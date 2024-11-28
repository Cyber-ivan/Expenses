import telebot
from handlers import command_handlers
from callback_handlers import register_callback_handlers
from config import BOT_TOKEN

token = BOT_TOKEN
bot = telebot.TeleBot(token)

command_handlers(bot)
register_callback_handlers(bot)


if __name__ == '__main__':
    bot.polling(none_stop=True)


















# import telebot
# import data_base.querys
# from config import BOT_TOKEN
# from telebot import types
# from data_base.database import DATABASE
# from handlers import command_handlers
# from callback_handlers import register_callback_handlers
# token = BOT_TOKEN
# bot = telebot.TeleBot(token)
# dataB = DATABASE()
# q = data_base.querys.Querys()
#
#
# # Переменные для отслеживания состояния
# awaiting_salary_amount = {}
# awaiting_expense_amount = {}
# awaiting_expense_table = {}
# table_bol = False
# expense_bol = False
#
# command_handlers(bot)
# register_callback_handlers(bot)
#
# @bot.message_handler(commands=['start'])
# def start_message(message):
#     answer = dataB.execute_query(q.user_exist(message))
#     if answer[0] == True:
#         initialize_main_buttons(message)
#     else:
#         bot.send_message(
#             message.chat.id,
#             text="Привет, {0.from_user.first_name}. "
#                  "\nВас нет в базе данных зарегистрированных пользователей, обратитсь к администратору"
#                  "\nВаш id {0.chat.id}".format(message),
#         )
#
#
# def initialize_main_buttons(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#     result_button = types.KeyboardButton("Итог")
#     add_money_button = types.KeyboardButton("Добавить зарплату")
#     check_category_button = types.KeyboardButton("Добавить расход")
#     name = ""
#     if message.from_user.first_name == "Ana":
#         name = "❤Настенька❤"
#     elif message.from_user.first_name == "Silence":
#         name = "Дима🦾"
#
#     markup.add(check_category_button, add_money_button, result_button)
#     bot.send_message(
#         message.chat.id,
#         text="Привет, {0} воспользуйся кнопками".format(name),
#         reply_markup=markup
#     )
#
#
# def main_menu(message):
#     global expense_bol, table_bol
#     initialize_main_buttons(message)
#     expense_bol = False
#     table_bol = False
#
#
# def result_button(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#     now_money_button = types.KeyboardButton("Текущие средства")
#     sum_expense_button = types.KeyboardButton("Сумма расходов за месяц")
#     sum_income_button = types.KeyboardButton("Сумма доходов за месяц")
#     table_month_button = types.KeyboardButton("Сводная таблица за месяц")
#     table_all_expenses_bytton = types.KeyboardButton("Сводная таблица за всё время")
#     main_menu_button = types.KeyboardButton("В главное меню")
#     markup.add(now_money_button, sum_expense_button, sum_income_button, table_month_button, table_all_expenses_bytton,
#                main_menu_button)
#     bot.send_message(
#         message.chat.id,
#         text="Выберите категорию итогов",
#         reply_markup=markup
#     )
#
#
# def add_money_button(message):
#     global awaiting_salary_amount
#     awaiting_salary_amount[message.chat.id] = True
#     bot.send_message(message.chat.id, text="Введите сумму зарплаты:")
#
#
# def now_money_button(message):
#     query = "SELECT SUM(money) FROM users;"
#     all_money = dataB.execute_query(query)
#     query = """SELECT
#                     (COALESCE((SELECT SUM(money) FROM expenses WHERE income = true), 0) -
#                     COALESCE((SELECT SUM(money) FROM expenses WHERE income = false), 0)) AS dif
#                 FROM expenses
#                 GROUP BY dif;"""
#     dif = dataB.execute_query(query)
#     all_money = float(all_money[0])
#     dif = float(dif[0])
#     bot.send_message(
#         message.chat.id,
#         text="Все средства: {0}\nДоходы - расходы: {1}".format(all_money, dif),
#     )
#
#
# def sum_expense_button(message):
#     query = """SELECT COALESCE(SUM(money),0) AS total_expenses
#     FROM expenses
#     WHERE income = false AND EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM CURRENT_DATE);"""
#     all_expenses = dataB.execute_query(query)
#     all_expenses = float(all_expenses[0])
#     query = """
#     SELECT COALESCE(
#         SUM(expenses.money),
#         0
#         ) AS total_expenses
#         FROM expenses
#         JOIN users ON users.id = expenses.uid
#         WHERE income = false
#           AND EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM CURRENT_DATE)
#           AND category_id = 4
#           AND telegram_id = {0};
#     """.format(message.chat.id)
#
#     my_expenses = dataB.execute_query(query)
#     my_expenses = float(my_expenses[0])
#     bot.send_message(
#         message.chat.id,
#         text="Мои расходы : {1}"
#              "\nОбщие расходы : {0}".format(all_expenses, my_expenses),
#     )
#
#
# def sum_income_button(message):
#     query = "SELECT SUM(money) FROM expenses WHERE income = true and (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE))"
#     all_income = dataB.execute_query(query)
#     all_income = float(all_income[0])
#     query = """SELECT  SUM(expenses.money) FROM expenses JOIN users ON users.id = expenses.uid WHERE income = false and (SELECT EXTRACT(MONTH FROM date)) = (SELECT EXTRACT(MONTH FROM CURRENT_DATE)) and telegram_id = {0};""".format(
#         message.chat.id)
#     my_income = dataB.execute_query(query)
#     my_income = float(my_income[0])
#     bot.send_message(
#         message.chat.id,
#         text="Мои доходы : {1}"
#              "\nОбщие доходы : {0}".format(all_income, my_income),
#     )
#
#
# def table_month_button(message):
#     global table_bol
#     table_bol = True
#     query = "SELECT name FROM categories;"
#     categories = dataB.execute_query(query)
#     category_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#     buttons_categories = []
#     for name in categories:
#         buttons_categories.append(types.KeyboardButton(name))
#     for i in buttons_categories:
#         category_markup.add(i)
#     main_menu_button = types.KeyboardButton("В главное меню")
#     category_markup.add(main_menu_button)
#     bot.send_message(
#         message.chat.id,
#         text="Выберете категорию для таблицы:",
#         reply_markup=category_markup
#     )
#
#
# def table_month_button_in_category(message):
#     query = """
#     SELECT
#        users.name AS name,
#        CASE
#            WHEN expenses.income = FALSE THEN expenses.money * -1
#            ELSE expenses.money
#        END AS money,
#        expenses.comment
#     FROM expenses
#     JOIN users ON users.id = expenses.uid
#     LEFT JOIN categories ON categories.id = expenses.category_id
#     WHERE EXTRACT(MONTH FROM expenses.date) = EXTRACT(MONTH FROM CURRENT_DATE) and categories.name = '{0}';
#     """.format(message.text)
#     table = dataB.fetch_dataframe(query)
#     query = """SELECT
#     SUM(
#         CASE
#             WHEN expenses.income = FALSE THEN expenses.money * -1
#             ELSE expenses.money
#         END
#     ) AS total_money
# FROM expenses
# JOIN users ON users.id = expenses.uid
# LEFT JOIN categories ON categories.id = expenses.category_id
# WHERE EXTRACT(MONTH FROM expenses.date) = EXTRACT(MONTH FROM CURRENT_DATE)
#   AND categories.name = '{0}';
# """.format(message.text)
#     sum_in_category = dataB.execute_query(query)
#     sum_in_category = float(sum_in_category[0])
#     bot.send_message(
#         message.chat.id,
#         text="Сводная таблица за месяц в категории {1} : \n{0} \nВсего: {2}".format(table, message.text,
#                                                                                     sum_in_category),
#     )
#     main_menu(message)
#
#
# def table_all_time_button(message):
#     query = """
#     SELECT
#        users.name AS name,
#        CASE
#            WHEN expenses.income = FALSE THEN expenses.money * -1
#            ELSE expenses.money
#        END AS money,
#        expenses.comment,
#        categories.name as category
#     FROM expenses
#     JOIN users ON users.id = expenses.uid
#     LEFT JOIN categories ON categories.id = expenses.category_id;
#     """
#     table = dataB.fetch_dataframe(query)
#     bot.send_message(
#         message.chat.id,
#         text="Сводная таблица за все время : \n{0}".format(table)
#     )
#
#
# def check_category_button(message):
#     global expense_bol
#     expense_bol = True
#     query = "SELECT name FROM categories;"
#     categories = dataB.execute_query(query)
#     category_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#     buttons_categories = []
#     for name in categories:
#         buttons_categories.append(types.KeyboardButton(name))
#     for i in buttons_categories:
#         category_markup.add(i)
#     main_menu_button = types.KeyboardButton("В главное меню")
#     category_markup.add(main_menu_button)
#     bot.send_message(
#         message.chat.id,
#         text="Выберите категорию расходов:",
#         reply_markup=category_markup
#     )
#
#
# @bot.message_handler(content_types=['text'])
# def buttons(message):
#     global awaiting_salary_amount, awaiting_expense_amount, awaiting_expense_table, expense_bol, table_bol
#     query = "SELECT name FROM categories;"
#     categories = dataB.execute_query(query)
#     if message.text == "Итог":
#         result_button(message)
#
#     elif message.text == "В главное меню":
#         main_menu(message)
#
#
#
#
#
#     elif message.text == "Добавить зарплату":
#         add_money_button(message)
#
#     elif message.text == "Добавить расход":
#         check_category_button(message)
#
#     elif message.text == "Текущие средства":
#         now_money_button(message)
#
#     elif message.text == "Сумма расходов за месяц":
#         sum_expense_button(message)
#
#     elif message.text == "Сумма доходов за месяц":
#         sum_income_button(message)
#
#     elif message.text == "Сводная таблица за месяц":
#         table_month_button(message)
#
#     elif message.text == "Сводная таблица за всё время":
#         table_all_time_button(message)
#
#
#     elif awaiting_salary_amount.get(message.chat.id):
#         try:
#             text = message.text
#             words = text.split()
#             money = float(words[0])
#             comment = ""
#             for word in words[1:]:
#                 comment += word + " "
#             transaction_query = """
#                         DO $$
#                         DECLARE
#                             user_id INT;
#                         BEGIN
#                             SELECT id INTO user_id
#                             FROM users
#                             WHERE telegram_id = {0};
#
#                             IF user_id IS NULL THEN
#                                 RAISE EXCEPTION 'Пользователь с telegram_id {0} не найден';
#                             END IF;
#
#                             -- Вычесть деньги из баланса пользователя
#                             UPDATE users
#                             SET money = money + {1}
#                             WHERE id = user_id;
#
#                             -- Добавить запись в таблицу expenses
#                             INSERT INTO expenses (uid, money, comment, income, date)
#                             VALUES (user_id, {1}, '{2}', TRUE, CURRENT_TIMESTAMP);
#                         END $$;
#                         """.format(message.chat.id, money, comment)
#             answer_db = dataB.execute_transaction(transaction_query)
#
#             bot.send_message(message.chat.id, text=answer_db)
#             initialize_main_buttons(message)
#         except ValueError:
#             bot.send_message(message.chat.id, text="Пожалуйста, введите корректное число.")
#         awaiting_salary_amount[message.chat.id] = False
#
#     elif awaiting_expense_amount.get(message.chat.id):
#         try:
#             text = message.text
#             words = text.split()
#             money = float(words[0])
#             comment = ""
#             for word in words[1:]:
#                 comment += word + " "
#             category = awaiting_expense_amount[message.chat.id]
#
#             transaction_query = """
#             DO $$
#             DECLARE
#                 user_id INT;
#                 category_id INT;
#             BEGIN
#                 -- Найти ID пользователя по telegram_id
#                 SELECT id INTO user_id
#                 FROM users
#                 WHERE telegram_id = {0};
#
#                 IF user_id IS NULL THEN
#                     RAISE EXCEPTION 'Пользователь с telegram_id {0} не найден';
#                 END IF;
#
#                 SELECT id INTO category_id
#                 FROM categories
#                 WHERE name = '{1}';
#
#                 IF category_id IS NULL THEN
#                     RAISE EXCEPTION 'Категория с именем {1} не найдена';
#                 END IF;
#
#                 -- Вычесть деньги из баланса пользователя
#                 UPDATE users
#                 SET money = money - {2}
#                 WHERE id = user_id;
#
#                 -- Добавить запись в таблицу expenses
#                 INSERT INTO expenses (uid, category_id, money, comment, income, date)
#                 VALUES (user_id, category_id, {2}, '{3}', FALSE, CURRENT_TIMESTAMP);
#             END $$;
#             """.format(message.chat.id, category, money, comment)
#             answer_db = dataB.execute_transaction(transaction_query)
#
#             bot.send_message(message.chat.id, text=answer_db)
#             initialize_main_buttons(message)
#
#         except ValueError:
#             bot.send_message(message.chat.id, text="Пожалуйста, введите корректное число.")
#         awaiting_expense_amount[message.chat.id] = None
#
#     elif message.text in categories and expense_bol == True:
#         awaiting_expense_amount[message.chat.id] = message.text
#         bot.send_message(message.chat.id, text="Введите сумму расходов для категории и комментарий:")
#
#     elif message.text in categories and table_bol == True:
#         table_month_button_in_category(message)
#         awaiting_expense_table[message.chat.id] = False
#         table_bol == False
#
#     else:
#
#         bot.send_message(message.chat.id, text="Я могу отвечать только на нажатие кнопок.")
#
#
# bot.polling(none_stop=True, interval=0)
