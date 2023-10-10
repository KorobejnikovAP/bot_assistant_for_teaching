from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update

from .structures import Role
from .fsm import AdminActions, Actions
from .keyboards import admin_action_keyboard, cancel_keyboard
from .start_comand import cmd_start
from db import User
from config_reader import config


admin_router = Router()


@admin_router.message(
    F.text == "Администратор",
    Actions.waiting_for_select_role,
)
async def select_action(message: Message, state: FSMContext, session_maker: sessionmaker):
    async with session_maker.begin() as session:
        qs = await session.scalars(
            select(User)
            .where(User.user_id == message.from_user.id)
        )
        user = qs.first()
        if not user or user.role != Role.ADMIN.value:
            await message.answer(
                text="Введите пароль администратора:",
                reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard, resize_keyboard=True)
            )
            await state.set_state(AdminActions.admin_waiting_for_password)
            return
        else:
            await message.answer(
                text="Здравствуйте, администратор!",
                reply_markup=ReplyKeyboardMarkup(keyboard=admin_action_keyboard, resize_keyboard=True)
            )
    await state.set_state(AdminActions.admin_waiting_for_text_action)


@admin_router.message(
    F.text == "Отменить действие",
    AdminActions.admin_waiting_for_password    
)
async def return_to_select_role(message: Message, state: FSMContext):
    await cmd_start(message, state)


@admin_router.message(
    AdminActions.admin_waiting_for_password
)
async def check_password(message: Message, state: FSMContext, session_maker: sessionmaker):
    if message.text == config.admin_password.get_secret_value():
        async with session_maker.begin() as session:
            qs = await session.scalars(
                select(User)
                .where(User.user_id == message.from_user.id)
            )
            user = qs.first()
            if not user:
                new_user = User(
                    user_id = message.from_user.id,
                    username = message.from_user.username,
                    role = Role.ADMIN.value,
                )
                session.add(new_user)
            else:
                await session.execute(
                    update(User)
                    .where(User.user_id == message.from_user.id)
                    .values(role=Role.ADMIN.value)
                    .execution_options(synchronize_session=None)
                )
        await message.answer(
            text="Вы вошли как администратор!",
            reply_markup=ReplyKeyboardMarkup(keyboard=admin_action_keyboard, resize_keyboard=True)
        )
        await state.set_state(AdminActions.admin_waiting_for_text_action)
    else:
        await message.answer(text="Пароль неверный! Введите снова:")


@admin_router.message(
    F.text == "Добавить преподавателя",
    AdminActions.admin_waiting_for_text_action
)
async def wait_nick(message: Message, state: FSMContext):
    await message.answer(
        text="Введите nickname пользователя",
        reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard, resize_keyboard=True))
    await state.set_state(AdminActions.admin_waiting_for_nick)


@admin_router.message(
    F.text == "Отменить действие", 
    AdminActions.admin_waiting_for_nick
)
async def return_to_select_action(message: Message, state: FSMContext):
    await cancel(message, state)


@admin_router.message(
    AdminActions.admin_waiting_for_nick
)
async def add_coach(message: Message, state: FSMContext, session_maker: sessionmaker):
    client = await TelegramClient(
        'bot',
        config.api_id.get_secret_value(),
        config.api_hash.get_secret_value()
    ).start(bot_token=config.bot_token.get_secret_value())

    async with client as session:
        user = await session(GetFullUserRequest(message.text))

    New_user = User(
        user_id = user.full_user.id,
        username = message.text,
        role = Role.COACH.value,
        admin_id = message.from_user.id
    )

    async with session_maker.begin() as session:
        qs = await session.scalars(select(User).where(User.user_id == New_user.user_id))
        check_user = qs.all()
        if len(check_user) == 0: 
            session.add(New_user)
            await message.answer("Преподаватель добавлен!")
        else:
            await message.answer("Этот преподаватель уже есть в базе!")
    await cancel(message, state)

    
@admin_router.message(
    F.text == "Удалить преподавателя",
    AdminActions.admin_waiting_for_text_action,
)
async def delete_coach_nick(message: Message, state: FSMContext, session_maker: sessionmaker):
    await message.answer(
        text="Введите username преподавтеля, которого собираетесь удалить: ",
        reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard, resize_keyboard=True)
    )
    await state.set_state(AdminActions.admin_waiting_for_nick_delete_coach)


@admin_router.message(
    F.text == "Отменить действие",
    AdminActions.admin_waiting_for_nick_delete_coach
)
async def return_to_select_action(message: Message, state: FSMContext):
    await cancel(message, state)


@admin_router.message(
    AdminActions.admin_waiting_for_nick_delete_coach
)
async def delete_coach(message: Message, state: FSMContext, session_maker: sessionmaker):
    client = await TelegramClient(
        'bot',
        config.api_id.get_secret_value(),
        config.api_hash.get_secret_value()
    ).start(bot_token=config.bot_token.get_secret_value())

    async with client as session:
        user = await session(GetFullUserRequest(message.text))
    
    async with session_maker.begin() as session:
        delete_user = (await session.scalars(select(User).where(User.user_id == user.full_user.id))).first()
        if delete_user:
            await session.delete(delete_user)
            await message.answer("Преподаватель удалён!")
        else:
            await message.answer("Этого преподавателя нет в базе!")
    await cancel(message, state)


async def cancel(message: Message, state: FSMContext):
    await state.set_state(AdminActions.admin_waiting_for_text_action)
    await message.answer(
        text="Что-нибудь ещё ?",
        reply_markup=ReplyKeyboardMarkup(keyboard=admin_action_keyboard, resize_keyboard=True)
    )