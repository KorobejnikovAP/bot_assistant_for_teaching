import datetime

from .base import BaseModel
from .record import Record
from sqlalchemy.types import BigInteger, Integer, VARCHAR, DATE
from sqlalchemy import Column, ForeignKey, select
from sqlalchemy.orm import relationship, sessionmaker

class User(BaseModel):

    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    username = Column(VARCHAR(32), unique=False, nullable=True)
    role = Column(Integer)

    #one to many
    coach_id = Column(BigInteger, ForeignKey("users.user_id"))
    student = relationship("User", foreign_keys=[coach_id])
    #one to many
    admin_id = Column(BigInteger, ForeignKey("users.user_id"))
    coach = relationship("User", foreign_keys=[admin_id])

    homeworks = relationship("HomeWork", back_populates="author")
    reg_date = Column(DATE, default=datetime.date.today())
    upd_date = Column(DATE, onupdate=datetime.date.today())

    """
    return list usernames 
    """
    @classmethod
    async def get_students_usernames(self, session_maker: sessionmaker, id_coach: int):
        async with session_maker.begin() as session:
            qs = await session.scalars(select(User).where(User.coach_id == id_coach))
            session.expunge_all()
        return qs
    
    def __str__(self) -> str:
        return f"<User:{self.user_id}>"