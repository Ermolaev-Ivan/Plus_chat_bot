import logging, datetime, configparser
from functions import ending as ending
from functions import ending2 as ending2
from aiogram import Bot, Dispatcher, executor, types



# Settings
config = configparser.ConfigParser()
config.read("config.ini")
API_TOKEN = config.get('Settings', 'token')
CHAT = config.getint('Settings', 'id_chat')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Global variables
count = 0
sportsmans = dict()
day = 0


@dp.message_handler()
async def plusBot(message: types.Message):
    global count
    global sportsmans
    global day

# первая реализация, самая простая, хорошо расширяемая, но не слишком элегантная
# нужно как то обойти тригер, а что более важно обойти ответ сообщением, который по сути и
# отправляет кнопки в телеграмм
#     if message.text == "/bot":
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         buttons = ["/who", "/get"]
#         keyboard.add(*buttons)
#         await message.answer("Опции", reply_markup=keyboard)

    buttons = ["/who", "/get"]
    markup = types.ReplyKeyboardMarkup().add(*buttons)

    # Собираем имена(ключи) спортсменов
    name_sportsman = message.from_user.last_name + " " + message.from_user.first_name

    # определяем в какой день сообщение отправлено
    message_day = message.date.strftime('%d')

    # механизм скидывания счетчика когда наступает новый день
    if message_day != day:
        count = 0
        sportsmans = dict()

    # если сообщение содержит "+" то происходит магия, а так же проверка чата, чтобы исключить обращения к боту в личку
    if message.text.find("+") != -1 and message.chat.id == CHAT:
        count = count + message.text.count("+")
        # Проверка,содержится ли плюсанувший челоек уже в словаре
        if name_sportsman in sportsmans.keys():
            sportsmans[name_sportsman] = sportsmans[name_sportsman] + message.text.count("+")
        else:
            sportsmans[name_sportsman] = message.text.count("+")
    # если в сообщении находятся только знак "-" и ключ уже есть в словаре то происходит магия
    elif "-" in message.text and name_sportsman in sportsmans.keys() and message.chat.id == CHAT:
        if message.text.count("-") == message.text.replace(" ", "").count("-"):
            if sportsmans[name_sportsman] == 1:
                sportsmans.pop(name_sportsman)
                count = count - 1
            elif sportsmans[name_sportsman] - message.text.count("-") <= 0:
                count = count - sportsmans[name_sportsman]
            else:
                count = count - message.text.count("-")
                sportsmans[name_sportsman] = sportsmans[name_sportsman] - message.text.count("-")

    # Команда выводящая количество идущих
    if message.text == "/get":
        if count == 0:
            await message.answer("На тренировку пока никто не собирается")
        else:
            await message.answer(f"На тренировку собирается {count} человек{ending(count)}")

    # Команда выводящая имена людей и кол-во приходящих с ними
    elif message.text == "/who":
        if count == 0:
            await message.answer("На тренировку пока никто не собирается")
        else:
            await message.answer("На тренировку пойдут:")
            for key in sportsmans.keys():
                if sportsmans[key] > 1:
                    await message.answer(f"{key} и приведет с собой еще {sportsmans[key] - 1}{ending2(sportsmans[key] - 1)}")
                else:
                    await message.answer(key)



    # перезаписываем глобальную переменную для работы логики сбрасыванию счетчиков
    day = datetime.datetime.now().strftime('%d')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
