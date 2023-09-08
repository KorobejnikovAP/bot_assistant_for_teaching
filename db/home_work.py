from sqlalchemy.types import BigInteger, Integer, VARCHAR, DATE, TEXT
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from .user import User

class HomeWork(BaseModel):

    __tablename__ = "homeworks"

    hw_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    author_id = Column(BigInteger, ForeignKey("users.user_id"))
    author = relationship("User", back_populates="homeworks")
    description = Column(TEXT)
    photo = Column(BYTEA)

    def __str__(self) -> str:
        return f"HW id: {self.hw_id}"
