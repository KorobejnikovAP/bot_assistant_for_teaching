from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from .fsm import StudentActions
from sqlalchemy.orm import sessionmaker

from config_reader import config

from sqlalchemy import select, update
from db import User, HomeWork
from .keyboards import student_action_keyboard
from .structures import TypeHwData
    

student_router = Router()


@student_router.message(
    F.text == "Ученик",
    StudentActions.waiting_for_select_role,
)
async def student_menu(message: Message, state: FSMContext):
    await state.update_data(role="ученик")
    await message.answer(
        text="Выберите дейтвие:", 
        reply_markup=ReplyKeyboardMarkup(
            keyboard=student_action_keyboard,
            resize_keyboard=True
        )
    )
    await state.set_state(StudentActions.student_waiting_for_text_action)


@student_router.message(
    F.text == "Получить д.з",
    StudentActions.student_waiting_for_text_action
)
async def student_select_action(message: Message, state: FSMContext, session_maker: sessionmaker):
    kb = []
    async with session_maker.begin() as session:
        user = (await session.scalars(select(User).where(User.user_id == message.from_user.id))).one()
        homeworks = (await session.scalars(select(HomeWork).where(HomeWork.author_id == user.coach_id))).all()
        for hw in homeworks:
            kb.append([KeyboardButton(text=hw.topic)])
   
    await message.answer(
        text="Выберете тему:",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )
    await state.set_state(StudentActions.student_waiting_for_select_theme)


@student_router.message(
    F.text[0] != '/',
    StudentActions.student_waiting_for_select_theme
)
async def student_select_theme(message: Message, state: FSMContext, session_maker: sessionmaker):
    
    theme = message.text
    async with session_maker.begin() as session:
        homework = (await session.scalars(select(HomeWork).where(HomeWork.topic == theme))).one()
        await message.answer(
            text=f"Описание: {homework.description}",
            reply_markup=ReplyKeyboardMarkup(keyboard=student_action_keyboard, resize_keyboard=True)
        )
        if homework.type_data == TypeHwData.PHOTO.value:
            await message.answer_photo(BufferedInputFile(homework.data, filename="file"))
        else:
            await message.answer_document(BufferedInputFile(homework.data, filename="file"))

    await state.set_state(StudentActions.student_waiting_for_text_action)


async def stop(message: Message, state: FSMContext):
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardMarkup(keyboard=student_action_keyboard, resize_keyboard=True)
    )
    await state.set_state(StudentActions.student_waiting_for_text_action)
