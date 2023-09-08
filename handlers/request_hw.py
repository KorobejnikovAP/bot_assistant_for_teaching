from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .start_comand import Actions
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from sqlalchemy import select

from db import User, HomeWork
    
roles = ["Преподаватель", "Ученик"]
request_router = Router()


@request_router.message(
    F.text == "Преподаватель",
    Actions.waiting_for_select_role,
)
async def coach_menu(message: Message, state: FSMContext, session_maker: sessionmaker):
    user = User(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )

    #Пользователь добавляется в базу, если его ещё там нет
    async with session_maker.begin() as session:
        if not session.execute(select(User).where(User == user)):
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


@request_router.message(
    F.text == "Добавить новое д.з",
    Actions.waiting_for_text,
)
async def coach_upload_hw(message: Message, state: FSMContext):
    await state.set_state(Actions.waiting_for_upload_hw)
    await message.answer(text="Загрузите файл с изображением")

@request_router.message(
    #F.photo,
    Actions.waiting_for_upload_hw,
)
async def coach_upload_hw(message: Message, state: FSMContext, session_maker: sessionmaker, bot:Bot):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    new_photo = (await bot.download_file(file_path)).read()

    hw = HomeWork(
        author_id=message.from_user.id,
        photo=new_photo
    )

    async with session_maker.begin() as session:
        session.add(hw)
    await state.set_state(Actions.end)
    await message.answer(text="Вы загрузили фото")


#@request_router.message(
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