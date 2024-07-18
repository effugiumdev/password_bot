import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from password_generator import XKCD
from bestconfig import Config
import requests
import hashlib

config = Config('./config.json')

logging.basicConfig(level=logging.DEBUG)
bot = telebot.TeleBot(token='YOU_TOKEN')

xkcd = XKCD('./words.txt')


@bot.message_handler(commands=['start'])
def start(msg: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"Words + ", callback_data="words_plus"))
    markup.add(InlineKeyboardButton(f'Words - ', callback_data='words_minus'))
    markup.add(InlineKeyboardButton(f'Remove_the_separators on/off', callback_data='divider'))
    markup.add(InlineKeyboardButton(f'Suffixes on/off', callback_data='suffix'))

    config.set('words_count', 2)
    config.set('delimiters', True)
    config.set('suffixes', True)

    bot.send_message(chat_id=msg.chat.id,
                     text='The initial number of words: 2\nUse the /generate command to create a password.',
                     reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data == "words_plus")
def words_plus(query: types.InlineQuery):
    count = config.get('words_count')

    if count >= 8:
        bot.send_message(query.from_user.id, 'Too many words')
        return

    if count < 2:
        bot.send_message(query.from_user.id, 'Too few words')
        return

    config.set('words_count', config.words_count + 1)

    bot.send_message(query.from_user.id, f'Now your words count in password is: {config.get('words_count')}')


@bot.callback_query_handler(lambda query: query.data == "words_minus")
def words_minus(query: types.InlineQuery):
    count = config.get('words_count')

    if count >= 8:
        bot.send_message(query.from_user.id, 'Too many words')
        return

    if count <= 2:
        bot.send_message(query.from_user.id, 'Too few words')
        return

    config.set('words_count', config.words_count - 1)

    bot.send_message(query.from_user.id, f'Now your words count in password is: {config.get('words_count')}')


@bot.callback_query_handler(lambda query: query.data == "divider")
def divider(query: types.InlineQuery):
    count = config.get('delimiters')

    if count == 1:
        bot.send_message(query.from_user.id, 'Delimiters: OFF')
        config.set('delimiters', False)
        return

    if count == 0:
        bot.send_message(query.from_user.id, 'Delimiters: ON')
        config.set('delimiters', True)
        return

    bot.send_message(query.from_user.id, f'Now your words count in password is: {config.get('delimiters')}')


@bot.callback_query_handler(lambda query: query.data == "suffix")
def suffix(query: types.InlineQuery):
    count = config.get('suffixes')

    if count == 1:
        bot.send_message(query.from_user.id, 'Suffixes: OFF')
        config.set('suffixes', False)
        return

    if count == 0:
        bot.send_message(query.from_user.id, 'Suffixes: ON')
        config.set('suffixes', True)
        return

    bot.send_message(query.from_user.id, f'Now your words count in password is: {config.get('suffixes')}')


@bot.message_handler(commands=['generate_weak'])
def weak(message: types.Message):
    weak = xkcd.weak()

    uniq = check_password_uniqueness(weak)
    bot.send_message(message.from_user.id, f'Your password: \n{weak}\n\n{uniq}')


@bot.message_handler(commands=['generate_normal'])
def normal(message: types.Message):
    normal = xkcd.normal()

    uniq = check_password_uniqueness(normal)
    bot.send_message(message.from_user.id, f'Your password: \n{normal}\n\n{uniq}')


@bot.message_handler(commands=['generate_strong'])
def strong(message: types.Message):
    strong = xkcd.strong()

    uniq = check_password_uniqueness(strong)
    bot.send_message(message.from_user.id, f'Your password: \n{strong}\n\n{uniq}')


@bot.message_handler(commands=['generate'])
def generate(message: types.Message, ):
    custom = xkcd.custom(prefixes=config.suffixes, separators=config.delimiters,
                         count=config.words_count)

    uniq = check_password_uniqueness(custom)
    bot.send_message(message.from_user.id, f'Your password: \n{custom}\n\n{uniq}')


def check_password_uniqueness(password):
    # Хешируем пароль с помощью SHA1
    sha1_password = hashlib.sha1(password.encode('utf-8', errors="ignore")).hexdigest().upper()

    # Отправляем GET-запрос к API Have I Been Pwned
    response = requests.get(f"https://api.pwnedpasswords.com/range/{sha1_password[:5]}")

    if response.status_code == 200:
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == sha1_password[5:]:
                return f"The password was found in data leaks {count} once.It is recommended to choose a different password."
        return "The password is unique and secure."
    else:
        return "The uniqueness of the password could not be verified."


@bot.message_handler(commands=['check'], )
def check(message: types.Message, ):
    args = message.text.split(" ")

    if len(args) < 2:
        bot.send_message(message.from_user.id, 'Password not entered. To use the command, enter the password.')

        return

    bot.send_photo(message.from_user.id, 'https://i.pinimg.com/originals/5a/c6/f5/5ac6f546be39abae59a76fa2a661915b.jpg',
                   'Password verification...')
    password = args[1]
    uniq = check_password_uniqueness(password)

    bot.send_message(message.from_user.id, uniq)


# Функция, которая вызывается при запуске приложения
def main():
    bot.polling(none_stop=True, interval=0)  # ПОД НЕЙ НИЧЕГО НЕ ПИСАТЬ, ТОЛЬКО СВЕРХУ


if __name__ == '__main__':
    main()
