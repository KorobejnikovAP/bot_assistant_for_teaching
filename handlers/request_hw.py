from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .start_comand import Actions
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db import User
    
roles = ["Преподаватель", "Ученик"]
router = Router()


@router.message(
    F.text == "Преподаватель",
    Actions.waiting_for_select_role,
)
async def coach_menu(message: Message, state: FSMContext, db_engine: AsyncEngine):
    user = User(
        user_id=12,
        username="пиво",
    )

    session_maker = sessionmaker(db_engine, class_=AsyncSession) 
    async with session_maker.begin() as session:
        session.add(user)
        
    kb = [
        [
            KeyboardButton(text="Добавить новое д.з"),
        ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(text="Выберите дейтвие:", reply_markup=keyboard) 
    state.update_data(role="преподаватель")
    await state.set_state(Actions.waiting_for_text)


#@router.message(
#    F.text == "Добавить новое д.з",
#    Actions.waiting_for_text,
#)
#def coach_upload_hw(message: Message, state: FSMContext):
    


#@router.message(
#    F.text == "Ученик",
#    Actions.waiting_for_select_role,
#)
#async def coach_menu(message: Message, state: FSMContext):
#    state.update_data(role="ученик")
#    kb = [
#        [
#            KeyboardButton(text="Получить д.з"),
#            KeyboardButton(text="Загрузить д.з"),
#        ]
#    ]
#    keyboard = ReplyKeyboardMarkup(
#        keyboard=kb,
#        resize_keyboard=True
#    )
#    await message.answer(
#        text="Выберите дейтвие:", 
#        reply_markup=keyboard
#    )
#    await state.set_state(Actions.choosing_action)
#    