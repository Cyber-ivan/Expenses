from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import data_base.querys
from config import BOT_TOKEN
from telebot import types
from data_base.database import DATABASE
from buttons import Buttons

q = data_base.querys.Querys()
dataB = DATABASE()
buttons = Buttons()

def command_handlers(bot: TeleBot):


    @bot.message_handler(commands=['start'])
    def start_message(message):
        answer = dataB.execute_query(q.user_exist(message))
        if answer[0][0] == True:
            initialize_main_buttons(message)
        else:
            bot.send_message(
                message.chat.id,
                text="Привет, {0.from_user.first_name}. "
                     "\nВас нет в базе данных зарегистрированных пользователей, обратитсь к администратору"
                     "\nВаш id {0.chat.id}".format(message),
            )

    def initialize_main_buttons(message):
        markup = buttons.main_menu()
        if message.from_user.first_name == "Ana":
            name = "❤Настенька❤"
        elif message.from_user.first_name == "Silence":
            name = "Дима🦾"
        bot.send_message(
            message.chat.id,
            text="Привет, {0} воспользуйся кнопками".format(name),
            reply_markup=markup
        )