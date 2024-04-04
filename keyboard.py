from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_buttons = [
    [KeyboardButton(text="Выбрать игру 🎰")],
    [KeyboardButton(text="Баланс 💰")],
    [KeyboardButton(text="Пополнить 💵"), KeyboardButton(text="Вывести 💸")]
]

games_buttons = [
    [KeyboardButton(text="CoinFlip 🍋")],
    [KeyboardButton(text="Назад")]
]

coinflip_buttons = [
    [KeyboardButton(text="Орел"), KeyboardButton(text="Решка")],
    [KeyboardButton(text="Назад")]
]

games_keyboard = ReplyKeyboardMarkup(keyboard=games_buttons, resize_keyboard=True)

coinflip_keyboard = ReplyKeyboardMarkup(keyboard=coinflip_buttons, resize_keyboard=True)

main_keyboard = ReplyKeyboardMarkup(keyboard=main_buttons, resize_keyboard=True)

back_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True)
