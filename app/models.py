from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)

    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(String, nullable=False)

    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)