import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties

# Токен бота (замените на свой)
TOKEN = "7436986076:AAGr3JjHSbBOf_K6eH6pG8sIyvpzq9aZUSc" 
admin_id = 7855386010

# Создаем объект бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Клавиатура с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏡 Интересует аренда / Interested in rent")],
        [KeyboardButton(text="🏠 Интересует покупка / Property purchase")],
        [KeyboardButton(text="📌 Нужен документ; Консультация / Need a document; Consultation")],
        [KeyboardButton(text="📞 Связаться с нами / Contact us")],
    ],
    resize_keyboard=True
)

# Храним последний выбор пользователя
user_requests = {}

# Функция для отправки сообщений админу
async def forward_to_admin(user_id):
"""Отправляет заявку от пользователя админу."""
if user_id not in user_requests:
return

    user_data = user_requests[user_id]
    username = f"@{user_requests[user_id]['username']}" if user_data['username'] else "Неизвестный пользователь"
    category = user_data['category']
    user_response = user_data.get('response', 'Нет ответа')

    text = (
        f"\U0001F514 Новая заявка от {username}:\n\n"
        f"\U0001F4CE Выбранная категория: {category}\n"
        f"\U0001F4DD Ответ клиента: {user_response}\n"
        )
    await bot.send_message(admin_id, text)
    
# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    text = (
        "Здравствуйте! Спасибо, что обратились к нам!\n\n"
        "Мы ценим доверие наших клиентов и предлагаем не только качественный подбор объектов, "
        "но и уникальные бонусы при сотрудничестве с нами.\n\n"
        "🎁 <b>Что вы получаете, работая с нами?</b>\n"
        "✅ Персональный подбор недвижимости по вашим критериям.\n"
        "✅ Доступ к эксклюзивным объектам, которых нет в открытом доступе.\n"
        "✅ Экономию времени – мы отбираем только лучшие варианты и организуем просмотры.\n"
        "✅ Юридическое сопровождение: консультации, проверка документов, поддержка на всех этапах сделки.\n\n"
        "• Бонусы от наших партнеров (приятные сюрпризы и скидки).\n"
        "• Najem okazjonalny - мы бесплатно подготовим документ для нотариального договора, если возникнет необходимость.\n"
        "• Персональный подарок от нашего агентства в знак благодарности за сотрудничество!\n\n"
        "Будем рады помочь!\n"
        "С уважением, <a href='https://t.me/savenkoestate'>Savenko.estate</a>. Чем мы можем вам помочь?"
    )
    await message.answer(text, reply_markup=keyboard)

# Функция для обработки кнопок
async def handle_category_selection(message: types.Message, category_text, response_text):
"""Сохраняет выбор пользователя и ждет ответа."""
    user_requests[message.from_user.id] = {
        "username": message.from_user.username,
        "category": category_text,
        "response": "Ожидаем ответ..."
        }
    await message.answer(response_text)
    
# Обработчики кнопок
@dp.message(lambda message: message.text == "🏡 Интересует аренда / Interested in rent")
async def rent_property(message: types.Message):
    await handle_category_selection(
        message,
        "Аренда недвижимости",
        "Отлично! Напишите, какую недвижимость ищете (квартира, дом, офис)? Ваш бюджет и параметры поиска?"
        )
    
@dp.message(lambda message: message.text == "🏠 Интересует покупка / Property purchase")
async def buy_property(message: types.Message):
    await handle_category_selection(
        message,
        "Покупка недвижимости",
        "Какую недвижимость хотите приобрести? Напишите бюджет и параметры."
        )
    
@dp.message(lambda message: message.text == "📌 Нужен документ; Консультация / Need a document; Consultation")
async def need_document(message: types.Message):
    await handle_category_selection(
        message,
        "Документы / Консультация",
        "Спасибо за отклик! Ваша заявка находится в обработке \U0001F64C В течение нескольких минут с вами свяжется наш менеджер. Благодарим за ожидание \U0001F4E9"
        )
    await asyncio.sleep(2)
    await forward_to_admin(message.from_user.id)
    
    
@dp.message(lambda message: message.text == "📞 Связаться с нами / Contact us")
async def contact_us(message: types.Message):
    await handle_category_selection(
        message,
        "Связь с менеджером",
        "Спасибо за отклик! Наш менеджер свяжется с вами в течение нескольких минут.\n"
                         "В случае задержки ответа - наш телефон для связи:\n"
                         "📞 Телефон: +48 576-363-332"
        )
    await asyncio.sleep(2)
    await forward_to_admin(message.from_user.id)

    # Обработчик сообщений после выбора кнопки
    @dp.message()
    async def process_user_response(message: types.Message):
"""Обрабатывает ответ пользователя после выбора категории."""
        user_id = message.from_user.id

        if user_id in user_requests:
            user_requests[user_id]['response'] = message.text
            await forward_to_admin(user_id)
            await message.answer("Спасибо за отклик! Ваша заявка находится в обработке \U0001F64C В течение нескольких минут с вами свяжется наш менеджер. Благодарим за ожидание \U0001F4E9")
            await message.answer("Выберите категорию выше, чтобы оставить заявку")

# Функция запуска бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
