import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN_CLIENT, TOKEN_EMPLOYEE

from customers.handlers import router as router_client
from employee.handlers import router as router_employee

from module_db.method_db import MethodDB

md = MethodDB()


async def main():
    # Ініціалізація ботів
    bot_client = Bot(token=TOKEN_CLIENT)
    bot_employee = Bot(token=TOKEN_EMPLOYEE)

    # Ініціалізація диспетчерів
    dp_client = Dispatcher()
    dp_employee = Dispatcher()

    # Додавання роутерів до диспетчерів
    dp_client.include_router(router_client)
    dp_employee.include_router(router_employee)

    # Старт поллінгу для обох ботів паралельно
    await asyncio.gather(
        dp_client.start_polling(bot_client),
        dp_employee.start_polling(bot_employee)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")


    # print(md.check_and_add_user(5086277204, None))
    # print(md.create_slot("12:00", "2024-05-29"))
    # print(md.book_slot(463210327,43, 1))
    # print(md.get_user_appointments(463210327))
    # md.get_available_slots()
    # print(md.get_busy_slots('2024-06-02'))
    # print(md.get_all_appointments("2024-06-06"))
    # print(md.get_free_slots("2024-06-06"))
    # print(md.get_services())
    # print(md.get_service_name(1))
