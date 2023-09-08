import datetime

from .base import BaseModel
from sqlalchemy.types import BigInteger, VARCHAR, DATE
from sqlalchemy import Column
from sqlalchemy.orm import relationship

class User(BaseModel):

    __tablename__ = "users"

    #telegram user_id
    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    #telegram username
    username = Column(VARCHAR(32), unique=False, nullable=True)
    homeworks = relationship("HomeWork", back_populates="author")

    reg_date = Column(DATE, default=datetime.date.today())
    upd_date = Column(DATE, onupdate=datetime.date.today())

    def __str__(self) -> str:
        return f"<User:{self.user_id}>"