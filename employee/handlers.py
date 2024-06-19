from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import module_keyboards.keyboards as kb
from module_db.method_db import MethodDB

router = Router()
db = MethodDB()


class MyShedule(StatesGroup):
    day = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    db.check_and_add_user(message.from_user.id, message.from_user.username)
    await message.answer(text=f"Вітаємо, {message.from_user.first_name}! Перегляньте свій розклад", reply_markup=kb.my_schedule)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(text=str(message.from_user.id))


@router.message(F.text == "Мій розклад")
async def chose_a_day(message: Message, state: FSMContext):
    await state.set_state(MyShedule.day)
    await message.answer(text=f"Оберіть день:", reply_markup=kb.free_days)


@router.callback_query(MyShedule.day)
async def chose_a_hour(callback: CallbackQuery, state: FSMContext):
    await state.update_data(day=callback.data)
    await callback.answer()
    await callback.message.answer(text=db.get_all_appointments(callback.data))
    await state.clear()
#
#
# @router.callback_query(MyShedule.service)
# async def chose_a_hour(callback: CallbackQuery, state: FSMContext):
#     await state.update_data(service=callback.data)
#     info = await state.get_data()
#     slot_id = db.create_slot(info["hour"], info["day"])
#     # запис клієнта на слот
#     db.book_slot(callback.from_user.id, slot_id, callback.data)
#
#     await callback.answer()
#     await callback.message.answer(db.get_the_text_of_the_record(info["hour"], info["day"], callback.data))
#     await state.clear()


