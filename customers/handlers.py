from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import module_keyboards.keyboards as kb
from module_db.method_db import MethodDB

router = Router()
db = MethodDB()


class TakeTurn(StatesGroup):
    day = State()
    hour = State()
    service = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    db.check_and_add_user(message.from_user.id, message.from_user.username)
    print(message.from_user.id)
    print(message.from_user.username)
    await message.answer(text="Вітаємо у нашій перукарні! Чим можемо допомогти?", reply_markup=kb.main)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(text = str(message))


@router.message(F.text == "Мої записи")
async def catalog(message: Message):
    info = db.get_user_appointments(message.from_user.id)  #"12:30 21.05.2024"
    await message.answer(text=f"Мої записи:\n{info}")


@router.message(F.text == "Записатись")
async def chose_a_day(message: Message, state: FSMContext):
    await state.set_state(TakeTurn.day)
    await message.answer(text=f"Оберіть день:", reply_markup=kb.free_days)


@router.callback_query(TakeTurn.day)
async def chose_a_hour(callback: CallbackQuery, state: FSMContext):
    await state.update_data(day=callback.data)
    await state.set_state(TakeTurn.hour)
    await callback.answer()
    free_slots = db.get_free_slots(callback.data)
    await callback.message.answer(text=f"Оберіть час:", reply_markup=kb.chose_a_hour(free_slots))


@router.callback_query(TakeTurn.hour)
async def chose_a_hour(callback: CallbackQuery, state: FSMContext):
    await state.update_data(hour=callback.data)
    await state.set_state(TakeTurn.service)
    await callback.answer()
    services = db.get_services()
    await callback.message.answer(text=f"Оберіть послугу:", reply_markup=kb.get_services(services))


@router.callback_query(TakeTurn.service)
async def chose_a_hour(callback: CallbackQuery, state: FSMContext):
    await state.update_data(service=callback.data)
    info = await state.get_data()
    slot_id = db.create_slot(info["hour"], info["day"])
    # запис клієнта на слот
    db.book_slot(callback.from_user.id, slot_id, callback.data)

    await callback.answer()
    await callback.message.answer(db.get_the_text_of_the_record(info["hour"], info["day"], callback.data))
    await state.clear()


