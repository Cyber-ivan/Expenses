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

