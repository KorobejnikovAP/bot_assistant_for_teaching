from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from .fsm import StudentActions
from sqlalchemy.orm import sessionmaker

from config_reader import config

from sqlalchemy import select, update
from db import User, HomeWork, Record
from .keyboards import student_action_keyboard, _cancel
from .structures import TypeHwData, Role
    

student_router = Router()


"""Входная точка для ученика"""
@student_router.message(
    F.text == "Ученик",
    StudentActions.waiting_for_select_role,
)
async def student_menu(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        qs = await session.scalars(select(User).where(User.user_id == message.from_user.id))
        user = qs.first()
        if not user:
            await message.answer(text="Вас нет в базе учеников, обратитесь к своему преподавателю")
        elif user.coach_id == None:
            await message.answer(text="Вы не являетесь учеником.")
        else:
            await message.answer(
                text="Выберите дейтвие:", 
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=student_action_keyboard,
                    resize_keyboard=True
                )
            )
            await state.set_state(StudentActions.student_waiting_for_text_action)
"""
Конец входной точки для ученика
"""



"""
Просмотр конспекта
"""
@student_router.message(
    F.text == "Посмотреть конспект", 
    StudentActions.student_waiting_for_text_action
)
async def student_records(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        qs = await session.scalars(select(Record).where(Record.student_id == message.from_user.id))
        records = [record.topic for record in qs.all()]
    kb = [[KeyboardButton(text=f"{i}")] for i in records]
    kb.append([KeyboardButton(text=_cancel)])
    await message.answer(
        text="Выбырете конспект", 
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )
    await state.set_state(StudentActions.student_waiting_for_select_record)


@student_router.message(
    F.text != _cancel,
    StudentActions.student_waiting_for_select_record
)
async def select_record(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        qs = await session.scalars(select(Record).where(Record.topic == message.text))
        record = qs.first()
        data = record.data
        await message.answer(
            text=record.topic,
            reply_markup=ReplyKeyboardMarkup(keyboard=student_action_keyboard, resize_keyboard=True)
        )
        await message.answer_document(BufferedInputFile(data, filename=f"{record.topic}.png"))
        await state.set_state(StudentActions.student_waiting_for_text_action)


@student_router.message(StudentActions.student_waiting_for_select_record)
async def stop_action(message: Message, state: FSMContext):
    await cancel(message, state)

"""
Конец просмотра конспекта
"""



"""
Просмотр домашнего задания
"""
@student_router.message(
    F.text == "Получить д.з",
    StudentActions.student_waiting_for_text_action
)
async def student_select_action(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        user = (await session.scalars(select(User).where(User.user_id == message.from_user.id))).first()
        homeworks_qs = await session.scalars(select(HomeWork).where(HomeWork.author_id == user.coach_id))
        homeworks_list = [hw.topic for hw in homeworks_qs.all()]
    kb = [[KeyboardButton(text=hw)] for hw in homeworks_list]
    kb.append([KeyboardButton(text=_cancel)])
    await message.answer(
        text="Выберете тему:",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )
    await state.set_state(StudentActions.student_waiting_for_select_theme)


@student_router.message(
    F.text != _cancel,
    StudentActions.student_waiting_for_select_theme
)
async def student_select_theme(message: Message, state: FSMContext, session_maker: sessionmaker): 
    theme = message.text
    async with session_maker.begin() as session:
        homework_qs = await session.scalars(select(HomeWork).where(HomeWork.topic == theme))
        homework = homework_qs.first()
        await message.answer(
            text=f"Описание: {homework.description}",
            reply_markup=ReplyKeyboardMarkup(keyboard=student_action_keyboard, resize_keyboard=True)
        )
        if homework.type_data == TypeHwData.PHOTO.value:
            await message.answer_photo(BufferedInputFile(homework.data, filename="file"))
        else:
            await message.answer_document(BufferedInputFile(homework.data, filename="file.txt"))
        await state.set_state(StudentActions.student_waiting_for_text_action)


@student_router.message(StudentActions.student_waiting_for_select_theme)
async def stop_action(message: Message, state: FSMContext):
    await cancel(message, state)

"""
Конец просмотра домашнего задания
"""



async def cancel(message: Message, state: FSMContext):
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardMarkup(keyboard=student_action_keyboard, resize_keyboard=True)
    )
    await state.set_state(StudentActions.student_waiting_for_text_action)
