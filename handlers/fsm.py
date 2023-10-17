from aiogram.fsm.state import State, StatesGroup

#состояния всех пользователей
class Actions(StatesGroup):
    waiting_for_select_role = State()
    

#состояния преподавателя
class CoachActions(Actions):
    waiting_for_text_action = State()
    waiting_for_topic = State()
    waiting_for_description = State()
    waiting_for_upload_hw = State()
    waiting_for_nick = State()
    waiting_for_select_student = State()
    waiting_for_upload_record = State()
    waiting_for_topic_record = State()

#состояния ученика
class StudentActions(Actions):
    student_waiting_for_text_action = State()
    student_waiting_for_select_theme = State()
    student_waiting_for_upload_hw = State()
    student_waiting_for_select_record = State()

#состояния администратора
class AdminActions(Actions):
    admin_waiting_for_password = State()
    admin_connection = State()
    admin_waiting_for_text_action = State()
    admin_waiting_for_nick = State()
    admin_waiting_for_nick_delete_coach = State()
