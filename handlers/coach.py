from aiogram import Router, F, Bot
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from .fsm import CoachActions
from sqlalchemy.orm import sessionmaker

from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

from config_reader import config

from sqlalchemy import select, update
from db import User, HomeWork
    

coach_router = Router()


@coach_router.message(
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
            KeyboardButton(text="Добавить ученика"),
        ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(text="Выберите дейтвие:", reply_markup=keyboard) 
    await state.update_data(role="преподаватель")
    await state.set_state(CoachActions.waiting_for_text_action)


@coach_router.message(
    F.text == "Добавить новое д.з",
    CoachActions.waiting_for_text_action,
)
async def coach_write_topic(message: Message, state: FSMContext):
    await message.answer(text="Напишите тему задания", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CoachActions.waiting_for_topic)


@coach_router.message(
    F.text == "Добавить ученика",
    CoachActions.waiting_for_text_action,
)
async def coach_write_nick(message: Message, state: FSMContext):
    await message.answer(
        text="Укажите никнейм ученика в телеграмме \n в формате @username:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CoachActions.waiting_for_nick)


@coach_router.message(
    CoachActions.waiting_for_nick
)
async def coach_add_student(message: Message, state: FSMContext, session_maker: sessionmaker):
    username = message.text
    client = await TelegramClient(
        'bot',
        config.api_id.get_secret_value(),
        config.api_hash.get_secret_value()
    ).start(bot_token=config.bot_token.get_secret_value())
    
    async with client as session:
        user = await session(GetFullUserRequest(username))

    new_user = User(
                user_id = user.full_user.id,
                username = username,
                coach_id = message.from_user.id
            )

    async with session_maker.begin() as session:
        qs = await session.scalars(select(User).where(User.user_id == new_user.user_id))
        check_user = qs.one()
        if not check_user:
            session.add(new_user)
            await message.answer(text="Вы добавили ученика")
        elif check_user.coach_id == None:
            await message.answer(text="Вы добавили ученика")
            await session.execute(
                update(User)
                .where(User.user_id == user.full_user.id)
                .values(coach_id=message.from_user.id)
                .execution_options(synchronize_session=None)
            )
        else:
            await message.answer(text="У этого ученика уже есть учитель!")


@coach_router.message(
    F.text[0] != '/',
    CoachActions.waiting_for_topic,
)
async def coach_write_description(message: Message, state: FSMContext, session_maker: sessionmaker):

    await state.update_data(topic=message.text)
    await message.answer(text="Опишите задание (вы сможете прикрепить файл на следующем шаге)")
    await state.set_state(CoachActions.waiting_for_description)


@coach_router.message(
    F.text[0] != '/',
    CoachActions.waiting_for_description,
)
async def coach_upload_file(message: Message, state: FSMContext, session_maker: sessionmaker):

    await state.update_data(description=message.text)
    await message.answer(text="Загрузите файл")
    await state.set_state(CoachActions.waiting_for_upload_hw)


@coach_router.message(
    F.content_type,
    CoachActions.waiting_for_upload_hw,
)
async def coach_end_upload_hw(message: Message, state: FSMContext, session_maker: sessionmaker, bot:Bot):
    if message.photo: file_id = message.photo[-1].file_id
    elif message.document: file_id = message.document.file_id
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
    await state.clear()
    await message.answer(text="Вы загрузили домашку")
