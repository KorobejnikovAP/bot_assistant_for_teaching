from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from .fsm import CoachActions
from sqlalchemy.orm import sessionmaker

from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

from config_reader import config

from sqlalchemy import select, update
from db import User, HomeWork, Record
from .keyboards import coach_action_keyboard, cancel_keyboard
from .structures import Role, TypeHwData
from .start_comand import cmd_cancel


coach_router = Router()


"""
Входная точка для преподавателя
"""
@coach_router.message(
    F.text == "Преподаватель",
    CoachActions.waiting_for_select_role,
)
async def coach_menu(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        if len((await session.scalars(
            select(User)
            .where(User.user_id == message.from_user.id)
            .where(User.role <= Role.COACH.value)
        )).all()) == 0:
            await message.answer("Вас нет в базе преподавателей! \nОбратитесь к админисстратору.")
            return 
    keyboard = ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
    await message.answer(text="Выберите дейтвие:", reply_markup=keyboard) 
    await state.update_data(role="преподаватель")
    await state.set_state(CoachActions.waiting_for_text_action)
"""
Конец входной точки для преподавателя
"""

 

"""
Выгрузика полного списка домашних заданий
"""
@coach_router.message(
    F.text == "Посмотреть список д.з",
    CoachActions.waiting_for_text_action,
)
async def homework_list(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        qs = await session.scalars(select(HomeWork).where(HomeWork.author_id == message.from_user.id))
        hw_list = list()
        for hw in qs.all():
            hw_list.append(hw.topic)
        if len(hw_list) > 0:
            ans = "Список ваших домашних работ:\n\t" + '\n\t'.join(hw_list)
        else:
            ans = "У вас нет домашних заданий!"
        await message.answer(text=ans)
"""
Конец выгрузки полного списка домашних заданий 
"""



"""
Добавление домашнего задания
"""
@coach_router.message(
    F.text == "Добавить новое д.з",
    CoachActions.waiting_for_text_action,
)
async def coach_write_topic(message: Message, state: FSMContext):
    await message.answer(
        text="Напишите тему задания",
        reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard, resize_keyboard=True)
    )
    await state.set_state(CoachActions.waiting_for_topic)


@coach_router.message(
    F.text != "Отменить действие",
    CoachActions.waiting_for_topic,
)
async def coach_write_description(message: Message, state: FSMContext, session_maker: sessionmaker):
    await state.update_data(topic=message.text)
    await message.answer(text="Опишите задание (вы сможете прикрепить файл на следующем шаге)")
    await state.set_state(CoachActions.waiting_for_description)


@coach_router.message(
    F.text != "Отменить действие",
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
    if message.photo: 
        file_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
        new_data = (await bot.download_file(file_info.file_path)).read()
        type_d = TypeHwData.PHOTO.value
    elif message.document: 
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        new_data = (await bot.download_file(file_path)).read()
        type_d = TypeHwData.Document.value
    else:
        await message.answer(text="Неподходящий формат")
        return

    hw_data = await state.get_data()

    hw = HomeWork(
        author_id=message.from_user.id,
        topic=hw_data["topic"],
        description=hw_data["description"],
        data=new_data,
        type_data=type_d
    )

    async with session_maker.begin() as session:
        session.add(hw)
    #await state.clear()
    await state.set_state(CoachActions.waiting_for_text_action)
    await message.answer(
        text="Вы загрузили домашку",
        reply_markup=ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
    )


@coach_router.message(CoachActions.waiting_for_description)
@coach_router.message(CoachActions.waiting_for_topic)
@coach_router.message(CoachActions.waiting_for_upload_hw)
async def return_to_select_action(message: Message, state: FSMContext):
    await cancel(message, state)
    
"""
Конец добавления домашнего задания
"""



"""
Добавление конспекта для ученика
"""
@coach_router.message(
    F.text == "Добавить конспект",
    CoachActions.waiting_for_text_action,
)
async def start_add_record(message: Message, state: FSMContext, session_maker: sessionmaker):
    students_list = await User.get_students_usernames(session_maker, message.from_user.id)
    ans = "Выберете ученика:"
    kb = [[KeyboardButton(text=f"{student.username}")] for student in students_list]
    kb.append([KeyboardButton(text="Отменить действие")])
    await message.answer(
        text=ans,
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )
    await state.set_state(CoachActions.waiting_for_select_student)


@coach_router.message(
    F.text != "Отменить действие", 
    CoachActions.waiting_for_select_student
)
async def select_student(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        qs = await session.scalars(select(User).where(User.username == message.text))
        student = qs.first()
        if student:
            await state.update_data(student_id=student.user_id)
            await state.set_state(CoachActions.waiting_for_topic_record)
            await message.answer(
                text="Напишите название конспекта",
                reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard, resize_keyboard=True),
            )
        else:
            await message.answer(text="Ошибка, ученик не найден.")


@coach_router.message(
    F.text != "Отменить действие", 
    CoachActions.waiting_for_topic_record
)
async def write_topic_for_record(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(CoachActions.waiting_for_upload_record)
    await message.answer(text="Загрузите файл с конспектом в формате .png")


@coach_router.message(
    F.text != "Отменить действие", 
    CoachActions.waiting_for_upload_record
)
async def upload_record(message: Message, state: FSMContext, session_maker: sessionmaker, bot: Bot):
    if message.document: 
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        new_data = (await bot.download_file(file_path)).read()
    state_data = await state.get_data()
    new_record = Record(
        author_id=message.from_user.id,
        student_id=state_data["student_id"],
        topic=state_data["topic"],
        data = new_data
    )    
    async with session_maker.begin() as sesison:
        try:
            sesison.add(new_record)
            await message.answer(
                text="Конспект загружен", 
                reply_markup=ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
            )
            await state.set_state(CoachActions.waiting_for_text_action)
        except:
            await message.answer(text="Что-то пошло не так(")

    
@coach_router.message(CoachActions.waiting_for_select_student)
@coach_router.message(CoachActions.waiting_for_upload_record)
@coach_router.message(CoachActions.waiting_for_topic_record)
async def return_to_select_action(message: Message, state: FSMContext):
    await cancel(message, state)

"""
Конец добавления конспекта для ученика
"""


"""
Посмотреть конспекты ученика
"""
@coach_router.message(
    F.text == "Посмотреть конспекты", 
    CoachActions.waiting_for_text_action
)
async def start_check_records():
    pass


"""
Добавление ученика
"""
@coach_router.message(
    F.text == "Добавить ученика",
    CoachActions.waiting_for_text_action,
)
async def coach_write_nick(message: Message, state: FSMContext):
    await message.answer(
        text="Укажите никнейм ученика в телеграмме \n в формате @username:",
        reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard, resize_keyboard=True)
    )
    await state.set_state(CoachActions.waiting_for_nick)


@coach_router.message(
    F.text != 'Отменить действие',
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
        check_user = qs.first()
        if not check_user:
            session.add(new_user)
            await message.answer(
                text="Вы добавили ученика", 
                reply_markup=ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
            )
        elif check_user.coach_id == None:
            await message.answer(
                text="Вы добавили ученика",
                reply_markup=ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
            )
            await session.execute(
                update(User)
                .where(User.user_id == user.full_user.id)
                .values(coach_id=message.from_user.id)
                .execution_options(synchronize_session=None)
            )
        else:
            await message.answer(
                text="У этого ученика уже есть учитель!",
                reply_markup=ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
            )
        await state.set_state(CoachActions.waiting_for_text_action)


@coach_router.message(CoachActions.waiting_for_nick)
async def return_to_select_action(message: Message, state: FSMContext):
    await cancel(message, state)

"""
Конец добавления ученика
"""



"""
Удаление ученика
"""
@coach_router.message(
    F.text == "Удалить ученика",
    CoachActions.waiting_for_text_action,
)
async def coach_select_nick_to_delete(message: Message, state: FSMContext, session_maker: sessionmaker):
    students_kb = []
    async with session_maker.begin() as session:
        students_qs = await session.scalars(select(User).where(User.coach_id == message.from_user.id))
        for student in students_qs:
            students_kb.append([KeyboardButton(text=student.username)])
    students_kb.append([KeyboardButton(text="Отменить действие")])
    await message.answer(
        text="Выберете ученика:",
        reply_markup=ReplyKeyboardMarkup(keyboard=students_kb, resize_keyboard=True)
    )
    await state.set_state(CoachActions.waiting_for_nick_to_delete)


@coach_router.message(
    F.text != "Отменить действие",
    CoachActions.waiting_for_nick_to_delete
)
async def delete_student(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        delete_user = (await session.scalars(select(User).where(User.username == message.text))).first()
        if delete_user is not None:
            await session.delete(delete_user)
            await message.answer(
                text="Ученик удалён", 
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=coach_action_keyboard, resize_keyboard=True
                )
            )
            await state.set_state(CoachActions.waiting_for_text_action)
        else:
            await message.answer(
                text="У вас нет такого ученика!", 
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=coach_action_keyboard, resize_keyboard=True
                )
            )
            await state.set_state(CoachActions.waiting_for_text_action)


@coach_router.message(CoachActions.waiting_for_nick_to_delete)
async def stop_delete(message: Message, state: FSMContext):
    await cancel(message, state)

"""
Конец удаления ученика
"""


async def cancel(message: Message, state: FSMContext):
    await state.set_state(CoachActions.waiting_for_text_action)
    await message.answer(
        text="Что-нибудь ещё ?",
        reply_markup=ReplyKeyboardMarkup(keyboard=coach_action_keyboard, resize_keyboard=True)
    )
