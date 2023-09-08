from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .start_comand import CoachActions, StudentActions
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from sqlalchemy import select

from db import User, HomeWork
    
roles = ["Преподаватель", "Ученик"]
request_router = Router()


@request_router.message(
    F.text == "Преподаватель",
    CoachActions.waiting_for_select_role,
)
async def coach_menu(message: Message, state: FSMContext, session_maker: sessionmaker):
    user = User(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )

    #Пользователь добавляется в базу, если его ещё там нет
    async with session_maker.begin() as session:
        if len((await session.scalars(select(User).where(User.user_id == user.user_id))).all()) == 0:
            session.add(user)
        
    kb = [
        [
            KeyboardButton(text="Добавить новое д.з"),
        ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(text="Выберите дейтвие:", reply_markup=keyboard) 
    state.update_data(role="преподаватель")
    await state.set_state(CoachActions.waiting_for_text_action)


@request_router.message(
    F.text == "Добавить новое д.з",
    CoachActions.waiting_for_text_action,
)
async def coach_upload_hw(message: Message, state: FSMContext):
    
    await message.answer(text="Напишите тему задания", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CoachActions.waiting_for_topic)


@request_router.message(
    F.text,
    CoachActions.waiting_for_topic,
)
async def coach_upload_hw(message: Message, state: FSMContext, session_maker: sessionmaker):

    await state.update_data(topic=message.text)
    await message.answer(text="Опишите задание (вы сможете прикрепить файл на следующем шаге)")
    await state.set_state(CoachActions.waiting_for_description)


@request_router.message(
    F.text,
    CoachActions.waiting_for_description,
)
async def coach_upload_hw(message: Message, state: FSMContext, session_maker: sessionmaker):

    await state.update_data(description=message.text)
    await message.answer(text="Загрузите файл")
    await state.set_state(CoachActions.waiting_for_upload_hw)


@request_router.message(
    #F.photo,
    CoachActions.waiting_for_upload_hw,
)
async def coach_upload_hw(message: Message, state: FSMContext, session_maker: sessionmaker, bot:Bot):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    new_photo = (await bot.download_file(file_path)).read()

    hw_data = await state.get_data()

    hw = HomeWork(
        author_id=message.from_user.id,
        topic=hw_data["topic"],
        description=hw_data["description"],
        photo=new_photo
    )

    async with session_maker.begin() as session:
        session.add(hw)
    await state.set_state(CoachActions.end)
    await message.answer(text="Вы загрузили домашку")



#хэндлеры для ученика 

@request_router.message(
    F.text == "Ученик",
    StudentActions.waiting_for_select_role,
)
async def student_menu(message: Message, state: FSMContext):
    state.update_data(role="ученик")
    kb = [
        [
            KeyboardButton(text="Получить д.з"),
            KeyboardButton(text="Загрузить д.з"),
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer(
        text="Выберите дейтвие:", 
        reply_markup=keyboard
    )
    await state.set_state(StudentActions.student_waiting_for_text_action)


@request_router.message(
    F.text == "Получить д.з",
    StudentActions.student_waiting_for_text_action
)
async def student_select_action(message: Message, state: FSMContext, session_maker: sessionmaker):
    
    kb = []

    async with session_maker.begin() as session:
        homeworks = (await session.scalars(select(HomeWork))).all()
        for hw in homeworks:
            kb.append(KeyboardButton(text=hw.topic))

    keyboard = ReplyKeyboardMarkup(
        keyboard=[kb],
        resize_keyboard=True
    )

    await message.answer(text="Выберете тему:", reply_markup=keyboard)
    await state.set_state(StudentActions.student_waiting_for_select_theme)


@request_router.message(
    F.text,
    StudentActions.student_waiting_for_select_theme
)
async def student_select_theme(message: Message, state: FSMContext, session_maker: sessionmaker):
    
    theme = message.text
    async with session_maker.begin() as session:
        homework = (await session.scalars(select(HomeWork).where(HomeWork.topic == theme))).one()
        await message.answer(text=f"Описание: {homework.description}")
        await message.answer_photo(BufferedInputFile(homework.photo, filename="image from buffer.jpg"))

    await state.set_state(StudentActions.student_waiting_for_text_action)