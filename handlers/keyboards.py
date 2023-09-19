from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

role_keyboard = [
        [
            KeyboardButton(text="Администратор"),
            KeyboardButton(text="Преподаватель"),
            KeyboardButton(text="Ученик")
        ]
    ]

coach_action_keyboard = [
        [
            KeyboardButton(text="Добавить новое д.з"),
            KeyboardButton(text="Добавить ученика"),
        ],
        [
            KeyboardButton(text="Посмотреть список д.з")
        ]
    ]

cancel_keyboard = [
    [
        KeyboardButton(text="Отменить действие")
    ]
]