
from .coach import coach_router
from .student import student_router
from .start_comand import start_router
from .admin import admin_router

from .structures import Role

routers = (start_router, coach_router, student_router, admin_router)