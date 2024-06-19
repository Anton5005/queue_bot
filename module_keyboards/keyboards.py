from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from datetime import datetime, timedelta

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Записатись"),
     KeyboardButton(text="Мої записи")]],
    resize_keyboard=True,
    input_field_placeholder="Оберіть пункт меню")

my_schedule = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Мій розклад")]],
    resize_keyboard=True,
    input_field_placeholder="Оберіть пункт меню")


catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="T-shirts", callback_data="t-shirts")],
    [InlineKeyboardButton(text="Pants", callback_data="pants")],
    [InlineKeyboardButton(text="Socks", callback_data="socks")]
])


get_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Send number", request_contact=True)]],
    resize_keyboard=True)


def choose_a_date():
    inline_keyboard = []
    # Отримати сьогоднішню дату
    today = datetime.today()
    # Вивести дати від сьогоднішньої до ще 7 днів вперед
    for i in range(5):  # 8, оскільки ми включаємо сьогоднішню дату плюс ще 7 днів
        current_date = today + timedelta(days=i)
        inline_keyboard.append([InlineKeyboardButton(text=current_date.strftime('%d.%m'),
                                                     callback_data=current_date.strftime('%Y-%m-%d'))])
    return inline_keyboard


free_days = InlineKeyboardMarkup(inline_keyboard=choose_a_date())


def chose_a_hour(free_slots):
    # buttons = []
    # for slot in free_slots:
    #     buttons.append([InlineKeyboardButton(text=slot, callback_data=slot)])
    # print(buttons)
    # return InlineKeyboardMarkup(inline_keyboard=buttons)
    buttons = []
    row = []  # Створюємо порожній рядок для кнопок
    for slot in free_slots:
        # Додаємо кнопку в поточний рядок
        row.append(InlineKeyboardButton(text=slot, callback_data=slot))
        # Якщо у поточному рядку вже 3 кнопки або ми досягли кінця доступних слотів, додаємо цей рядок до кнопок
        if len(row) == 3 or slot == free_slots[-1]:
            buttons.append(row)
            row = []  # Очищаємо рядок для наступних кнопок
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# def free_hour(slot_date):
#     return InlineKeyboardMarkup(inline_keyboard=chose_a_hour(slot_date))

def get_services(services):
    buttons = []
    for service_id, service_name in services.items():
        buttons.append([InlineKeyboardButton(text=service_name, callback_data=str(service_id))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


