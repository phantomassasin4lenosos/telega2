import asyncio
import sqlite3 as sq
import decimal
import random

from decimal import Decimal
from database import db, cur, registration, balance, blockname
from config import access_token, welcome_text, payments_token, coinflip_x
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram import Bot, Dispatcher, F
from keyboard import main_keyboard, back_button, games_keyboard, coinflip_keyboard

bot = Bot(token=access_token)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def get_start(message: Message):
    try:
        cur.execute(f"INSERT INTO users (user_id) VALUES ({message.from_user.id})")
        db.commit()

        await message.answer(welcome_text, reply_markup=main_keyboard)

    except sq.IntegrityError:
        await message.answer("Главное меню:", reply_markup=main_keyboard)


@dp.message(F.text == "Баланс 💰")
async def get_balance(message: Message):
    if registration(message.from_user.id):
        await message.answer(f"Ваш баланс: {balance(message.from_user.id)}₽")


@dp.message(F.text == "Выбрать игру 🎰")
async def get_games(message: Message):
    if registration(message.from_user.id):
        cur.execute(f"UPDATE users SET blockname = 'games' WHERE user_id == {message.from_user.id}")
        db.commit()

        await message.answer("Выберите игру: ", reply_markup=games_keyboard)


@dp.message(F.text == "Пополнить 💵")
async def get_deposit(message: Message):
    if registration(message.from_user.id):
        cur.execute(f"UPDATE users SET blockname = 'deposit' WHERE user_id == {message.from_user.id}")
        db.commit()

        await message.answer(f"Введите сумму на которую хотите пополнить баланс: ", reply_markup=back_button)


@dp.message(F.text == "Назад")
async def get_back(message: Message):
    if registration(message.from_user.id):
        if blockname(message.from_user.id) in ["games", "deposit"]:
            cur.execute(f"UPDATE users SET blockname = 'main' WHERE user_id == {message.from_user.id}")
            await message.answer("Главное меню:", reply_markup=main_keyboard)

        elif blockname(message.from_user.id) in ["coinflip", "cf_bet1", "cf_bet2"]:
            cur.execute(f"UPDATE users SET blockname = 'games' WHERE user_id == {message.from_user.id}")
            await message.answer("Выберите игру: ", reply_markup=games_keyboard)

        db.commit()


@dp.message(F.text == "CoinFlip 🍋")
async def get_coinflip(message: Message):
    if registration(message.from_user.id):
        cur.execute(f"UPDATE users SET blockname = 'coinflip' WHERE user_id == {message.from_user.id}")
        db.commit()

        await message.answer("Сделайте ставку: Орел / Решка", reply_markup=coinflip_keyboard)


@dp.message(F.text == "Орел")
@dp.message(F.text == "Решка")
async def get_coinflip_bet(message: Message):
    if registration(message.from_user.id):
        if blockname(message.from_user.id) in ["coinflip", "cf_bet1", "cf_bet2"]:
            if message.text == "Орел":
                cur.execute(f"UPDATE users SET blockname = 'cf_bet1' WHERE user_id == {message.from_user.id}")

            elif message.text == "Решка":
                cur.execute(f"UPDATE users SET blockname = 'cf_bet2' WHERE user_id == {message.from_user.id}")

            await message.answer(f"Ваша ставка: {message.text}\nВаш баланс: {balance(message.from_user.id)}₽\n\nВедите сумму ставки:")
            db.commit()


@dp.message(F.text)
async def get_text(message: Message):
    if registration(message.from_user.id):
        if blockname(message.from_user.id) == "deposit":    # DEPOSIT
            try:
                deposit = Decimal(message.text).quantize(Decimal("1.00"), rounding=decimal.ROUND_DOWN)

                if deposit < Decimal("100"):
                    await message.answer("Минимальная сумма депозита: 100.00₽")

                elif Decimal(message.text).quantize(Decimal("1.00"), rounding=decimal.ROUND_UP) > Decimal("1000000"):
                    await message.answer("Максимальная сумма депозита: 1000000.00₽")

                else:
                    await bot.send_invoice(
                        message.from_user.id,
                        prices=[LabeledPrice(label=f"AMG4GAMES ПОПОЛНЕНИЕ БАЛАНСА", amount=int(deposit * 100))],
                        provider_token=payments_token,
                        title=f"Пополнение баланса",
                        description=f"\n",
                        payload="AMG4GAMES",
                        currency="rub")

            except decimal.InvalidOperation:
                await message.answer("Некорректная сумма депозита")

        elif blockname(message.from_user.id) in ["cf_bet1", "cf_bet2"]:
            try:
                bet = Decimal(message.text).quantize(Decimal("1.00"))
                cf_random = random.randint(1, 2)

                if bet < Decimal("0.01"):
                    await message.answer("Минимальная сумма ставки: 0.01₽")

                elif bet > balance(message.from_user.id):
                    await message.answer(f"Недостаточно средств. Ваш баланс: {balance(message.from_user.id)}₽")

                else:
                    cf_result = "Орел" if cf_random == 1 else "Решка"
                    if blockname(message.from_user.id) == f"cf_bet{cf_random}":
                        cur.execute(f"UPDATE users SET balance = {balance(message.from_user.id) + bet * Decimal(coinflip_x)} WHERE user_id == {message.from_user.id}")
                        await message.answer(f"Вы выйграли: {(bet * Decimal(coinflip_x)).quantize(Decimal("1.00"))}₽ ✅\nРезультат игры: {cf_result}\n\nВаш баланс: {balance(message.from_user.id)}₽")

                    else:
                        cur.execute(f"UPDATE users SET balance = {balance(message.from_user.id) - bet} WHERE user_id == {message.from_user.id}")
                        await message.answer(f"Вы проиграли: {bet}₽ ❌\nРезультат игры: {cf_result}\n\nВаш баланс: {balance(message.from_user.id)}₽")

                    db.commit()

            except decimal.InvalidOperation:
                await message.answer("Некорректная сумма ставки")


@dp.pre_checkout_query(lambda query: True)
async def get_pay(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
    cur.execute(f"UPDATE users SET balance = balance + {pre_checkout_q.total_amount / 100} WHERE user_id == {pre_checkout_q.from_user.id}")
    cur.execute(f"UPDATE users SET deposit = deposit + {pre_checkout_q.total_amount / 100} WHERE user_id == {pre_checkout_q.from_user.id}")
    db.commit()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
