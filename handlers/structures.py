from enum import Enum

class Role(Enum):
    ADMIN = 0
    COACH = 1
    STUDENT = 2

class TypeHwData(Enum):
    PHOTO = 0
    Document = 1