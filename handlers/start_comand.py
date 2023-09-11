from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

#состояния всех пользователей
class Actions(StatesGroup):
    waiting_for_select_role = State()

#состояния преподавателя
class CoachActions(Actions):
    waiting_for_text_action = State()
    waiting_for_topic = State()
    waiting_for_description = State()
    waiting_for_upload_hw = State()
    waiting_for_nick = State()

#состояния ученика
class StudentActions(Actions):
    student_waiting_for_text_action = State()
    student_waiting_for_select_theme = State()
    student_waiting_for_upload_hw = State()


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
    await state.set_state(CoachActions.waiting_for_select_role)


@start_router.message(Command(commands=["cancel"]))
@start_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )