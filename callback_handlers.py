from telebot import TeleBot
from buttons import Buttons
from tabulate import tabulate
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from data_base.database import DATABASE
from data_base.querys import Querys

states = {"is_income": False, "is_expense": False}
category_expense = ""


def register_callback_handlers(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        global states, category_expense
        db = DATABASE()
        q = Querys()
        buttons = Buttons()
        user_id = call.from_user.id
        data = call.data
        match data:

            case "add_income":
                states["is_income"] = True
                markup = InlineKeyboardMarkup()
                main_menu_button = types.InlineKeyboardButton("В главное меню", callback_data="main_menu")
                markup.add(main_menu_button)
                bot.edit_message_text(
                    text="Введите доход и комментарий",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    message_id=call.message.message_id,  # ID сообщения
                    reply_markup=markup
                )

            case "add_expense":
                states["is_expense"] = True
                markup = buttons.expense_or_income_category_menu()
                bot.edit_message_text(
                    text="Выбери категорию расходов",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    message_id=call.message.message_id,  # ID сообщения
                    reply_markup=markup  # Новая клавиатура
                )

            case "summary":
                markup = buttons.summary_menu()
                bot.edit_message_text(
                    text="Выбери категорию",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    message_id=call.message.message_id,  # ID сообщения
                    reply_markup=markup  # Новая клавиатура
                )

            case "main_menu":
                markup = buttons.main_menu()
                name = call.from_user.first_name
                if name == "Ana":
                    name = "❤Настенька❤"
                elif name == "Silence":
                    name = "Дима🦾"
                for key in states:
                    states[key] = False
                bot.edit_message_text(
                    text="Привет, {0} воспользуйся кнопками".format(name),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            case "now_money":
                all_money = db.execute_query(q.sum_money_users())
                dif = db.execute_query(q.difference_income_expense())
                all_money = float(all_money[0][0])
                dif = float(dif[0][0])
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    text="Все средства: {0}\nДоходы - расходы: {1}".format(all_money, dif),
                    message_id=call.message.message_id
                )
                markup = buttons.summary_menu()
                bot.send_message(
                    text="Выбери категорию",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    reply_markup=markup  # Новая клавиатура
                )

            case "sum_expense":
                all_expenses = db.execute_query(q.all_expenses_on_month())
                my_expenses = db.execute_query(q.all_user_expenses_for_the_month(call.message.chat.id))
                all_expenses = float(all_expenses[0][0])
                my_expenses = float(my_expenses[0][0])
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Мои расходы : {1}"
                         "\nОбщие расходы : {0}".format(all_expenses, my_expenses),
                )
                markup = buttons.summary_menu()
                bot.send_message(
                    text="Выбери категорию",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    reply_markup=markup  # Новая клавиатура
                )

            case "sum_income":
                my_income = db.execute_query(q.all_user_income_for_the_month(call.message.chat.id))
                all_income = db.execute_query(q.all_income_on_month())
                my_income = float(my_income[0][0]) if my_income and my_income[0][0] is not None else 0.0
                all_income = float(all_income[0][0]) if all_income and all_income[0][0] is not None else 0.0

                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Мои доходы : {1}"
                         "\nОбщие доходы : {0}".format(all_income, my_income),
                )
                markup = buttons.summary_menu()
                bot.send_message(
                    text="Выбери категорию",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    reply_markup=markup  # Новая клавиатура
                )

            case "table_month":
                markup = buttons.expense_or_income_category_menu("table_month")
                bot.edit_message_text(
                    text="Выбери категорию рсаходов",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    message_id=call.message.message_id,  # ID сообщения
                    reply_markup=markup  # Новая клавиатура
                )

            case "table_all_expenses":
                table = db.fetch_dataframe(q.table_expense_all_time())
                formatted_table = tabulate(
                    table,
                    headers="keys",  # Используем названия колонок как заголовки
                    tablefmt="pretty"  # Формат таблицы (можно заменить на "plain", "fancy_grid" и т.д.)
                )
                bot.edit_message_text(
                    text="Сводная таблица за все время : \n\n{0}".format(formatted_table),
                    chat_id=call.message.chat.id,  # ID чата
                    message_id=call.message.message_id,  # ID сообщения

                )
                markup = buttons.summary_menu()
                bot.send_message(
                    text="Выбери категорию",  # Текст сообщения
                    chat_id=call.message.chat.id,  # ID чата
                    reply_markup=markup  # Новая клавиатура
                )
            case "":
                pass
        categories = db.execute_query(q.categories_name())

        for tup in categories:
            for category in tup:
                if data == "table_month:{0}".format(category):
                    table = db.fetch_dataframe(q.table_expense_on_month(category))
                    formatted_table = tabulate(
                        table,
                        headers="keys",  # Используем названия колонок как заголовки
                        tablefmt="pretty"  # Формат таблицы (можно заменить на "plain", "fancy_grid" и т.д.)
                    )
                    bot.edit_message_text(
                        text="Сводная таблица месяц по {0} : \n\n{1}".format(category, formatted_table),
                        chat_id=call.message.chat.id,  # ID чата
                        message_id=call.message.message_id,  # ID сообщения

                    )
                    markup = buttons.summary_menu()
                    bot.send_message(
                        text="Выбери категорию",  # Текст сообщения
                        chat_id=call.message.chat.id,  # ID чата
                        reply_markup=markup  # Новая клавиатура
                    )
                elif data == "expense:{0}".format(category):
                    category_expense = category
                    markup = InlineKeyboardMarkup()
                    main_menu_button = types.InlineKeyboardButton("В главное меню", callback_data="main_menu")
                    markup.add(main_menu_button)
                    bot.edit_message_text(
                        text="Введите сумму и комментарий для расхода в категории:{0}".format(category),
                        # Текст сообщения
                        chat_id=call.message.chat.id,  # ID чата
                        message_id=call.message.message_id,  # ID сообщения
                        reply_markup=markup
                    )

    @bot.message_handler(content_types=['text'])
    def user_query(message):
        global category_expense
        buttons = Buttons()
        db = DATABASE()
        q = Querys()
        users_tg_id = db.execute_query(q.users_telegram_id())
        users_tg_id_list = [row[0] for row in users_tg_id]




        if states["is_income"] == True:
            bot.delete_message(message.chat.id, message.id - 1)
            result = db.execute_transaction(q.transaction_income(message))
            bot.send_message(
                text=result,
                chat_id=message.chat.id,  # ID чата
            )
            markup = buttons.main_menu()
            bot.send_message(
                text="Выбери категорию",  # Текст сообщения
                chat_id=message.chat.id,  # ID чата
                reply_markup=markup  # Новая клавиатура
            )
            for id in users_tg_id_list:
                if id in users_tg_id_list:
                    continue
                else:
                    bot.send_message(
                        text="Пользователь {0} заработал {1}".format(message.from_user.first_name,message.text),  # Текст сообщения
                        chat_id=id,  # ID чата
                    )

        elif states["is_expense"] == True:
            bot.delete_message(message.chat.id, message.id - 1)
            result = db.execute_transaction(q.transaction_expenses(message, category_expense))
            category_expense = ""
            bot.send_message(
                text=result,
                chat_id=message.chat.id,  # ID чата
            )
            markup = buttons.main_menu()
            bot.send_message(
                text="Выбери категорию",  # Текст сообщения
                chat_id=message.chat.id,  # ID чата
                reply_markup=markup  # Новая клавиатура
            )
            for id in users_tg_id_list:
                if id in users_tg_id_list:
                    continue
                else:
                    bot.send_message(
                        text="Пользователь {0} потратил {1}".format(message.from_user.first_name,message.text),  # Текст сообщения
                        chat_id=id,  # ID чата
                    )
        else:
            markup = InlineKeyboardMarkup()
            main_menu_button = types.InlineKeyboardButton("В главное меню", callback_data="main_menu")
            markup.add(main_menu_button)
            bot.send_message(
                text="Выберите категорию расходов/доходов или обратитесь к администратору с наездом",
                chat_id=message.chat.id,
                reply_markup=markup
            )

#
# from telebot import TeleBot
# from states import get_state, set_state, States
# from keyboards.main_menu import main_menu
# from keyboards.sub_menu import sub_menu
#
# def register_callback_handlers(bot: TeleBot):
#     @bot.callback_query_handler(func=lambda call: True)
#     def callback_handler(call):
#         user_id = call.from_user.id
#         current_state = get_state(user_id)
#
#         if call.data == "button_1":
#             if current_state == States.DEFAULT:
#                 bot.answer_callback_query(call.id, "Вы выбрали Кнопку 1 в состоянии DEFAULT.")
#                 set_state(user_id, States.CHOICE_ONE)
#                 bot.edit_message_text("Вы выбрали Кнопку 1. Теперь вы в состоянии CHOICE_ONE.",
#                                       chat_id=call.message.chat.id,
#                                       message_id=call.message.message_id,
#                                       reply_markup=sub_menu())
#             elif current_state == States.CHOICE_ONE:
#                 bot.answer_callback_query(call.id, "Вы снова нажали Кнопку 1, но уже в состоянии CHOICE_ONE.")
#
#         elif call.data == "button_2":
#             if current_state == States.DEFAULT:
#                 bot.answer_callback_query(call.id, "Вы выбрали Кнопку 2 в состоянии DEFAULT.")
#                 set_state(user_id, States.CHOICE_TWO)
#                 bot.edit_message_text("Вы выбрали Кнопку 2. Теперь вы в состоянии CHOICE_TWO.",
#                                       chat_id=call.message.chat.id,
#                                       message_id=call.message.message_id,
#                                       reply_markup=sub_menu())
#             elif current_state == States.CHOICE_TWO:
#                 bot.answer_callback_query(call.id, "Вы снова нажали Кнопку 2, но уже в состоянии CHOICE_TWO.")
#
#     @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
#     def back_to_main_handler(call):
#         user_id = call.from_user.id
#         set_state(user_id, States.DEFAULT)
#         bot.edit_message_text("Вы вернулись в главное меню.",
#                               chat_id=call.message.chat.id,
#                               message_id=call.message.message_id,
#                               reply_markup=main_menu())
