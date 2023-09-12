import datetime

from .base import BaseModel
from sqlalchemy.types import BigInteger, Integer, VARCHAR, DATE
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

class User(BaseModel):

    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    username = Column(VARCHAR(32), unique=False, nullable=True)
    role = Column(Integer, nullable=False)

    #one to many
    coach_id = Column(BigInteger, ForeignKey("users.user_id"))
    student = relationship("User")

    homeworks = relationship("HomeWork", back_populates="author")

    reg_date = Column(DATE, default=datetime.date.today())
    upd_date = Column(DATE, onupdate=datetime.date.today())

    def __str__(self) -> str:
        return f"<User:{self.user_id}>"