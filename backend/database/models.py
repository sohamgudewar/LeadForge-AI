from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text


class Base(DeclarativeBase):
    pass


class Lead(Base):

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)

    company = Column(String)

    knowledge = Column(Text)

    research = Column(Text)

    enrichment = Column(Text)

    lead_score = Column(Text)

    personalization = Column(Text)

    email = Column(Text)

    review = Column(Text)
