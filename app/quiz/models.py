from dataclasses import dataclass
from typing import Optional


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Question:
    title: str
    id: Optional[int]
    theme_id: Optional[int]
    answers: list[Answer]
