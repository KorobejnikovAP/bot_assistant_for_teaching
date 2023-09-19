from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from .structures import Role
from .fsm import AdminActions
from .keyboards import admin_action_keyboard
from db import User
from config_reader import config


admin_router = Router()


@admin_router.message(
    F.text == "Администратор",
    AdminActions.waiting_for_select_role,
)
async def select_action(message: Message, state: FSMContext, session_maker: sessionmaker):

    #-------  проверить принадлежность роли администатора

    keyboard = ReplyKeyboardMarkup(
        keyboard=admin_action_keyboard, 
        resize_keyboard=True
    )
    await message.answer(
        text="Выберите действие:", 
        reply_markup=keyboard
    )
    await state.set_state(AdminActions.admin_waiting_for_text_action)


@admin_router.message(
    F.text == "Добавить преподавателя",
    AdminActions.admin_waiting_for_text_action
)
async def wait_nick(message: Message, state: FSMContext):
    await message.answer(text="Введите nickname пользователя")
    await state.set_state(AdminActions.admin_waiting_for_nick)


@admin_router.message(
    AdminActions.admin_waiting_for_nick,
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
        role = Role.COACH.value
    )

    async with session_maker.begin() as session:
        qs = await session.scalars(select(User).where(User.user_id == New_user.user_id))
        check_user = qs.all()
        if len(check_user) == 0: 
            session.add(New_user)
            await message.answer("Преподаватель добавлен!")
        else:
            await message.answer("Этот преподаватель уже есть в базе!")

    
@admin_router.message(
    F.text == "Удалить преподавателя",
    AdminActions.admin_waiting_for_text_action,
)
async def delete_coach(message: Message, state: FSMContext, session_maker: sessionmaker):
    pass
