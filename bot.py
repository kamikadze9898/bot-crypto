import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "7537615401:AAHs03_8a572MidL_3wdHexpqaIH_zC22WQ"
ADMIN_ID = -1002544079940  # ID адміна
NOTION_LINK = "https://ivy-height-7a0.notion.site/1ec3a0a9187080ada9c4dfb2a113b80f?pvs=4"  # Ссылка на шаблон

# Створюємо об'єкт бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Кнопки
def get_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Оплатити", callback_data="pay")
    return kb.as_markup()

def get_confirm_keyboard(user_id, confirmed=None):
    """ Генерация клавиатуры для подтверждения """
    if confirmed is None:
        return InlineKeyboardMarkup(inline_keyboard=[ 
            [InlineKeyboardButton(text="✅ Підтвердити оплату", callback_data=f"confirm:{user_id}")],
            [InlineKeyboardButton(text="❌ Оплата не пройшла. Спробуйте ще раз", callback_data=f"retry:{user_id}")],
        ])
    elif confirmed:
        return InlineKeyboardMarkup(inline_keyboard=[ 
            [InlineKeyboardButton(text="✅ Оплата підтверджена ✅", callback_data="confirmed")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[ 
            [InlineKeyboardButton(text="❌ Оплата не пройшла. Спробуйте ще раз", callback_data=f"retry:{user_id}")],
        ])

# Команда /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "<b>🚀 Вступай у світ криптовалют з нашим шаблоном Notion!</b>\n\n"
        
        "<i>Хочеш розібратися в крипті? Наш шаблон — це ідеальний старт для новачка!</i> 💡\n\n"
        
        "<b>🔍 Що ти отримаєш:</b>\n\n"
        
        "• <b>Пояснення криптовалюти простими словами:</b> Що таке крипта, блокчейн, токени та біткоїн. Все доступно! 🔑\n\n"
        
        "• <b>Кроки для початку:</b> Як створити криптогаманець, користуватися MetaMask, Binance, OKX, і купувати крипту 💳\n\n"
        
        "• <b>Ідеї для заробітку:</b> Airdrops, фармінг, ICO — знайди для себе можливості заробітку! 💰\n\n"
        
        "• <b>Як вивести крипту:</b> Покрокові інструкції з покупки, обміну та виведення в гривні або долари 💸\n\n"
        
        "<b>Це твій перший крок до фінансової свободи! Почни заробляти вже зараз! 🚀</b>\n\n"
        
        "<b>Натискай кнопку, щоб придбати шаблон:</b> 👇",
        reply_markup=get_main_keyboard()
    )

# Кнопка "Оплатити"
@dp.callback_query(F.data == "pay")
async def show_payment_info(callback: CallbackQuery):
    # Удаляем старое сообщение
    await callback.message.delete()

    # Отправляем новое сообщение
    await callback.message.answer(
    "<b>Реквізити для оплати:</b>\n\n"
    "<i>Щоб скопіювати, просто натисніть на номер карти.</i>\n\n"
    
    "<b>🔹 Картка:</b> <code>4149 4990 9532 4495</code>\n"
    "<b>🔹 Сума:</b> <u>10$ = 400грн</u>\n\n"
    
    "📝 <i>Після оплати, будь ласка, надішліть скріншот вашої оплати ⬇️</i>\n\n"
    
    "<b>❗️ Не забувайте перевірити правильність реквізитів!</b>"
)

# Обработка фото
@dp.message(F.photo)
async def handle_photo(message: Message):
    # Сохраняем фото
    bot.temp_photo = message.photo[-1].file_id
    bot.temp_user = message.from_user.id

    # Не удаляем фото
    # Удаляем только текстовое сообщение, если оно не фото
    if message.content_type == 'text':
        await message.delete()

    # Отправляем ответ
    await message.answer(
    "📸 <b>Скріншот отримано!</b>\n\n"
    "Тепер, будь ласка, введи останні <b>4 цифри картки</b>, з якої ти здійснив оплату.\n\n"
    "<i>Це необхідно для перевірки транзакції.</i>"
)

# Обработка цифр карты
@dp.message(F.text)
async def handle_card_digits(message: Message):
    if not hasattr(bot, 'temp_photo') or not hasattr(bot, 'temp_user'):
        await message.answer("❗️ Спочатку надішли скріншот оплати.")
        return

    digits = message.text

    # Перевірка на кількість цифр
    if len(digits) != 4 or not digits.isdigit():
        await message.answer("❗️ Введіть саме 4 цифри картки. Спробуйте ще раз.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "Без username"
    
    # Відправка адміну з фото та інформацією
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=bot.temp_photo,
        caption=(f"💰 <b>Нова оплата!</b>\n\n"
                 f"👤 Користувач: {username}\n"
                 f"🆔 ID: <code>{message.from_user.id}</code>\n"
                 f"💳 4 цифри картки: <b>{digits}</b>"),
        reply_markup=get_confirm_keyboard(message.from_user.id)
    )

    await message.answer(
    "<b>🔍 Ваша заявка зараз на перевірці.</b>\n\n"
    "<i>Будь ласка, очікуйте підтвердження від адміністратора.</i> ⏳\n\n"
    "<i>Заявки перевіряються з <b>09:00 до 00:00</b>.\n"
    "Якщо ваша заявка була надіслана після <b>00:00</b>, вона буде оброблена і підтверджена о <b>09:00</b>.</i>\n\n"
    "Не хвилюйтеся, все буде перевірено та підтверджено вчасно. Дякуємо за терпіння!"
)

# Підтвердження оплати
@dp.callback_query(F.data.startswith("confirm:"))
async def confirm_payment(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    
    # Генерируем клавиатуру для подтверждения
    new_keyboard = get_confirm_keyboard(user_id, confirmed=True)
    
    # Проверяем, совпадает ли новая клавиатура с текущей
    if callback.message.reply_markup != new_keyboard:
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    
    await bot.send_message(user_id, f"✅ Оплату підтверджено! Ось твій шаблон:\n{NOTION_LINK}\n\n"
    "<b>🎉 Вітаємо з покупкою!</b>\n\n"
    "<i>Ваш шаблон успішно придбано! 🛒</i>\n\n"
    "<b>Щоб відкрити ваш шаблон:</b>\n"
    "<i>1️⃣ Перейдіть за цим посиланням, щоб відкрити шаблон у Notion:</i>\n\n"
    "<i>2️⃣ Натисніть на кнопку <b>«Duplicate»</b>, щоб додати шаблон до свого облікового запису Notion.</i>\n\n"
    "<i>3️⃣ Після цього ви зможете використовувати шаблон безпосередньо у своєму акаунті! ✨</i>\n\n"
    "<b>💡 Не забудьте налаштувати шаблон під себе!</b>\n\n"
    "<b>🙏 Дякуємо за покупку! Ми впевнені, що цей шаблон допоможе вам досягти нових висот у криптовалютному світі!</b>\n\n"
    "<b>🚀 Бажаємо великих успіхів та профітів! 💸</b>"
)
    await callback.answer("Користувачу надіслано шаблон ✅")

# Повідомлення про невдалу оплату
@dp.callback_query(F.data.startswith("retry:"))
async def retry_payment(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    # Отправляем пользователю сообщение и кнопку для повторной оплаты
    await bot.send_message(
        user_id,
        "❌ <b>Оплата не пройшла.</b>\n\n"
    "<i>На жаль, ваш платіж не був знайдений у системі.</i>\n\n"
    "🔄 <b>Будь ласка, спробуйте ще раз.</b>\n\n"
    "❓ Якщо виникли проблеми — <b>ми зв'яжемося з вами</b>.\n\n"
    "💬 Ми завжди раді допомогти!",
        reply_markup=get_main_keyboard()  # Отправляем только кнопку "Оплатити"
    )
    
    # Генерируем клавиатуру для повторной оплаты (с кнопкой "Повторити оплату")
    new_keyboard = get_confirm_keyboard(user_id, confirmed=False)
    
    # Проверяем, не совпадает ли новая клавиатура с текущей
    if callback.message.reply_markup != new_keyboard:
        # Обновляем клавиатуру, если она отличается от текущей
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)

    await callback.answer("Користувачу надіслано повідомлення для повтору оплати.")

# Запуск
async def main():
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("Polling was canceled")

if __name__ == "__main__":
    asyncio.run(main())
