from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from .fsm import Actions
from .keyboards import role_keyboard


start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=role_keyboard,
        resize_keyboard=True,
        input_field_placeholder="Кто ты ?"
    )
    await message.answer(
        "Привет! Выбери свою роль)",
        reply_markup=keyboard
    )
    await state.set_state(Actions.waiting_for_select_role)


@start_router.message(Command(commands=["cancel"]))
@start_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Вы вышли из аккаунта! \nВоспользуйтесь командой /start, чтобы продолжить работу.",
        reply_markup=ReplyKeyboardRemove()
    )
