from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

_cancel = "Отменить действие"

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
        [KeyboardButton(text="Посмотреть список д.з")],
        [KeyboardButton(text="Добавить новое д.з")],
        [KeyboardButton(text="Добавить конспект")],
        [KeyboardButton(text="Добавить ученика")],
        [KeyboardButton(text="Удалить ученика")],
    ]

student_action_keyboard = [
        [KeyboardButton(text="Получить д.з")],
        [KeyboardButton(text="Посмотреть конспект")]
    ]

cancel_keyboard = [
    [KeyboardButton(text=_cancel)]
]