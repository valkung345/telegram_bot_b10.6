import telebot
from telebot import types

from config import TOKEN, keys
from extensions import APIException, Converter

bot = telebot.TeleBot(TOKEN)


# создание клавиатуры
def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = []
    for key in keys.keys():
        if key != base:
            buttons.append(types.KeyboardButton(key.capitalize()))
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=["start", "help"])
def handle_start_help(message: telebot.types.Message):
    text = "Чтобы начать введите команду:\n" \
           "<имя валюты> <в какую валюту переводить> <количество переводимой валюты>,\n" \
           "например: доллар рубль 100\n" \
           "\n" \
           "Так же вы можете переводить валюту с помощь /convert\n" \
           "\n" \
           "Список доступных команд:\n" \
           "/convert - начать конвертацию валют\n" \
           "/help, /start - помощь по боту\n" \
           "/values - показать доступные валюты\n" \
           "/info - о программе"
    bot.reply_to(message, text)


@bot.message_handler(commands=["values"])
def handle_values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for key in keys.keys():
        text += '\n' + key
    bot.reply_to(message, text)


@bot.message_handler(commands=["info"])
def handle_info(message: telebot.types.Message):
    text = 'Простой бот, для конвертации валют.\n' \
           '/help или /start - для знакомства с ботом.\n' \
           'Автор - Гладков Алексей'
    bot.reply_to(message, text)


@bot.message_handler(commands=["convert"])
def convert_handler(message: telebot.types.Message):
    text = "Введите валюту, из которой конвертировать"
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)


def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    text = "Введите валюту, в которую конвертировать"
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, quote_handler, base)


def quote_handler(message: telebot.types.Message, base):
    quote = message.text.strip().lower()
    text = "Введите количество конвертируемой валюты"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, quote)


def amount_handler(message: telebot.types.Message, base, quote):
    amount = message.text.strip().replace(",", ".")

    try:
        total_base = Converter.get_price(base, quote, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка ввода параметров!\n{e}')
    else:
        amount = float(amount)
        text = f"Результат конвертации:\n" \
               f"{amount:,.2f} {base} = {total_base:,.2f} {quote}\n" \
               f"{amount:,.2f} {keys[base]} = {total_base:,.2f} {keys[quote]}"
        bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=["text"])
def handle_convert(message: telebot.types.Message):
    values = message.text.lower().replace(",", ".").split()

    try:
        if len(values) != 3:
            raise APIException("Не верное количество параметров")
        base, quote, amount = values
        total_base = Converter.get_price(base, quote, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка ввода параметров!\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду:\n{e}')
    else:
        amount = float(amount)
        text = f"Результат конвертации:\n" \
               f"{amount:,.2f} {base} = {total_base:,.2f} {quote}\n" \
               f"{amount:,.2f} {keys[base]} = {total_base:,.2f} {keys[quote]}"
        bot.send_message(message.chat.id, text)


# bot.polling(non_stop=True)
bot.infinity_polling()
