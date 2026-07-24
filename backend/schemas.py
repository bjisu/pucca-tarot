"""API 요청/응답 Pydantic 스키마."""
from typing import List, Optional

from pydantic import BaseModel, Field


class CardOut(BaseModel):
    id: int
    number: int
    name_kr: str
    name_en: str
    arcana: str
    suit: Optional[str] = None
    image: str
    meaning: str
    reading_sentence: str
    keywords: List[str]


class ReadingRequest(BaseModel):
    question: str = Field(default="", max_length=300)
    uuid: Optional[str] = None


class TodayReadingResponse(BaseModel):
    reading_type: str = "today"
    crisis: bool = False
    question: str
    card: CardOut
    one_line: str
    interpretation: str
    advice: str
    llm_provider: str


class PositionReading(BaseModel):
    position: str
    card: CardOut
    interpretation: str


class ClassicReadingResponse(BaseModel):
    reading_type: str = "classic"
    crisis: bool = False
    question: str
    positions: List[PositionReading]
    overall: str
    advice: str
    llm_provider: str


class CrisisResponse(BaseModel):
    crisis: bool = True
    message: str
