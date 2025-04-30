import asyncio
import logging
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from aiogram.client.default import DefaultBotProperties

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

prices = [LabeledPrice(label="Поддержать проект ⭐️", amount=1)]

START_PHOTO_URL = os.getenv("PHOTO_START")
ABOUT_PHOTO_URL = os.getenv("PHOTO_INFO")
HELP_PHOTO_URL = os.getenv("PHOTO_HELP")
DONATE_PHOTO_URL = os.getenv("PHOTO_DONATE")
THANKS_PHOTO_URL = os.getenv("PHOTO_THANKS")
ERROR_PHOTO_URL = os.getenv("PHOTO_ERROR")

SAPPORT_URL = os.getenv("SUPPORT_URL")

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть мини-приложение", url="https://t.me/your_app?start=miniapp")],
        [InlineKeyboardButton(text="О нас", callback_data="about"),
        InlineKeyboardButton(text="Помощь", callback_data="help")],
        [InlineKeyboardButton(text="Поддержать проект ⭐️", callback_data="pay")],
    ])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back")]
])


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await bot.delete_webhook(drop_pending_updates=True)
    await message.answer_photo(
        photo=START_PHOTO_URL,
        caption=(f"Привет, <b>User</b>! 👋\n\n"
        f"Добро пожаловать в Capybara Marketplace\n\n"
        f"Здесь вы можете покупать и продавать товары, "
        f"общаться с продавцами и находить лучшие предложения.\n\n"
        f"Нажмите кнопку ниже, чтобы открыть приложение:"),
        reply_markup=start_keyboard()
    )


@dp.callback_query(F.data == "about")
async def callback_about(query: types.CallbackQuery):
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=ABOUT_PHOTO_URL,
            caption=(
        f"<b>Расскажу немного про сервис Capybara Marketplace</b>\n\n"
        f"Capybara Marketplace — это современный маркетплейс, созданный для удобной покупки и продажи товаров через Telegram.\n"
        f"Больше не нужно искать товары в десятках различных групп и чатах — мы собрали все в одном месте.\n\n"
        
        f"👥 Уже более ХХХХ пользователей пользуются нашим сервисом.\n"
        f"📈 У нас более ХХХХ объявлений в ХХХ различных категориях.\n"
        f"🏘 Мы работаем в ХХХХ городах Аргентины.\n\n"
        
        f"Мы стремимся предоставить удобный и безопасный сервис как для покупателей, так и для продавцов.\n"
        f"Цени свое время — используй его с пользой.\n\n"
        
        f"Если у вас возникли вопросы, напишите нам <a href='{SAPPORT_URL}'>Команда Capybara</a>"
    )
        ),
        reply_markup=back_kb
    )
    await query.answer()


@dp.callback_query(F.data == "help")
async def callback_help(query: types.CallbackQuery):
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=HELP_PHOTO_URL,
            caption=(
        "🔍 <b>Справка по использованию Capybara</b>\n\n"
        "Для использования сервиса Capybara Marketplace вам не нужна регистрация или авторизация. Все, что вам нужно — это открыть приложение и наслаждаться покупками и продажами.\n"
        "Мы используем только официальные технологии Telegram и не храним никакой информации о вас.\n"
        "Мы применяем систему рейтингов для продавцов, поэтому вы можете не только сортировать товары по цене, но и обращать внимание на рейтинг продавцов, что сделает вашу покупку более безопасной.\n"
        "А самое главное — мы экономим ваше время на поиске товаров.\n\n"
        
        "Дополнительные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/info - Информация о сервисе\n\n"
        f"Если у вас возникли вопросы, напишите нам <a href='{SAPPORT_URL}'>Команда Capybara</a>"
    )
        ),
        reply_markup=back_kb
    )
    await query.answer()


@dp.callback_query(F.data == "pay")
async def callback_pay(query: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=query.message.chat.id,
        title="Донат проекту",
        description="Все собранные средства пойдут на развитие проекта. Спасибо за Ваше доверие!",
        payload="donate_payload",
        provider_token="",  
        currency="XTR",
        prices=prices,
    )
    await query.answer()


@dp.pre_checkout_query(F.invoice_payload == "donate_payload")
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    total = message.successful_payment.total_amount / 100
    await message.answer_photo(
        photo=THANKS_PHOTO_URL,
        caption=f"Спасибо за донат ⭐️ {total:.2f} XTR! Ваша поддержка бесценна.",
        reply_markup=back_kb
    )


@dp.callback_query(F.data == "back")
async def callback_back(query: types.CallbackQuery):
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=START_PHOTO_URL,
            caption=(f"Привет, <b>User</b>! 👋\n\n"
        f"Добро пожаловать в Capybara Marketplace\n\n"
        f"Здесь вы можете покупать и продавать товары, "
        f"общаться с продавцами и находить лучшие предложения.\n\n"
        f"Нажмите кнопку ниже, чтобы открыть приложение:")
        ),
        reply_markup=start_keyboard()
    )
    await query.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
