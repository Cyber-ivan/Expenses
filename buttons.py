from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from data_base.database import DATABASE
from telebot import types
import telebot
from config import BOT_TOKEN
from telebot import types
from data_base.database import DATABASE
from data_base.querys import Querys

data = DATABASE()
q = Querys()


class Buttons():

    def expense_or_income_category_menu(self, type="expense"):
        markup = InlineKeyboardMarkup()
        categories = data.execute_query(q.categories_name())
        for tup in categories:
            for name in tup:
                markup.add(InlineKeyboardButton(name, callback_data=f"{type}:{name}"))
        main_menu_button = types.InlineKeyboardButton("В главное меню", callback_data="main_menu")
        markup.add(main_menu_button)
        return markup

    def main_menu(self):
        markup = InlineKeyboardMarkup()
        add_expense_button = types.InlineKeyboardButton("Добавить расход", callback_data="add_expense")
        add_income_button = types.InlineKeyboardButton("Добавить зарплату", callback_data="add_income")
        summary_button = types.InlineKeyboardButton("Итог", callback_data="summary")
        markup.add(add_expense_button, add_income_button)
        markup.add(summary_button)
        return markup

    def summary_menu(self):
        markup = InlineKeyboardMarkup()
        now_money_button = types.InlineKeyboardButton("Текущие средства", callback_data="now_money")
        sum_expense_button = types.InlineKeyboardButton("Сумма расходов за месяц", callback_data="sum_expense")
        sum_income_button = types.InlineKeyboardButton("Сумма доходов за месяц", callback_data="sum_income")
        table_month_button = types.InlineKeyboardButton("Сводная таблица за месяц", callback_data="table_month")
        table_all_expenses_bytton = types.InlineKeyboardButton("Сводная таблица за всё время",
                                                               callback_data="table_all_expenses")
        main_menu_button = types.InlineKeyboardButton("В главное меню", callback_data="main_menu")
        markup.add(now_money_button)
        markup.add(sum_expense_button)
        markup.add(sum_income_button)
        markup.add(table_month_button)
        markup.add(table_all_expenses_bytton)
        markup.add(main_menu_button)
        return markup
