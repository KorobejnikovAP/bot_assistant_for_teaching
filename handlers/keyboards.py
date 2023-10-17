from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

role_keyboard = [
        [KeyboardButton(text="Администратор")],
        [KeyboardButton(text="Преподаватель")],
        [KeyboardButton(text="Ученик")]
    ]

admin_action_keyboard = [
        [KeyboardButton(text="Добавить преподавателя")],
        [KeyboardButton(text="Удалить преподавателя")]
    ]

coach_action_keyboard = [
        [KeyboardButton(text="Добавить новое д.з")],
        [KeyboardButton(text="Добавить конспект")],
        [KeyboardButton(text="Добавить ученика")],
        [KeyboardButton(text="Посмотреть список д.з")]
    ]

student_action_keyboard = [
        [KeyboardButton(text="Получить д.з")],
        [KeyboardButton(text="Посмотреть конспект")]
    ]

cancel_keyboard = [
    [KeyboardButton(text="Отменить действие")]
]