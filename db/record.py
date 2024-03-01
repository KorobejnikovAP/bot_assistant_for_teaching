from sqlalchemy.types import BigInteger, Integer, VARCHAR, DATE, TEXT
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy import Column, ForeignKey, select
from sqlalchemy.orm import relationship, sessionmaker
from .base import BaseModel


class Record(BaseModel):

    __tablename__ = "records"

    record_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    author_id = Column(BigInteger, ForeignKey("users.user_id"))
    author = relationship("User", foreign_keys=[author_id])
    student_id = Column(BigInteger, ForeignKey("users.user_id"))
    student = relationship("User", foreign_keys=[student_id])
    topic = Column(VARCHAR(50))
    data = Column(BYTEA)

    @classmethod
    async def get_student_records(self, session_maker: sessionmaker, id_student: int):
        async with session_maker.begin() as session:
            records = await session.scalars(select(Record).where(Record.student_id==id_student))
            session.expunge_all()
        return records
    
    def __str__(self) -> str:
        return f"Record id: {self.record_id}"
