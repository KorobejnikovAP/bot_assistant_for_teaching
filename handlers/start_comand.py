from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class Actions(StatesGroup):
    waiting_for_select_role = State()
    waiting_for_text = State()
    waiting_for_upload_hw = State()
    end = State()

start_router = Router()

@start_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = [
        [
            KeyboardButton(text="Преподаватель"),
            KeyboardButton(text="Ученик")
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Кто ты ?"
    )
    await message.answer(
        "Привет! Выбери свою роль)",
        reply_markup=keyboard
    )
    await state.set_state(Actions.waiting_for_select_role)
