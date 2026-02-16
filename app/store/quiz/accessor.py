from app.base.base_accessor import BaseAccessor
from app.quiz.models import Answer, Question, Theme
from tests.app.quiz import question2dict


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = Theme(id=self.app.database.next_theme_id, title=title)
        self.app.database.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Theme | None:
        for theme in self.app.database.themes:
            if title == theme.title:
                return theme
        return None

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        for theme in self.app.database.themes:
            if id_ == theme.id:
                return theme
        return None

    async def list_themes(self) -> list[Theme]:
        return self.app.database.themes

    async def get_question_by_title(self, title: str) -> Question | None:
        for question in self.app.database.questions:
            if question.title == title:
                return question
        return None

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        question = Question(
            title=title,
            id=self.app.database.next_question_id,
            theme_id=theme_id,
            answers=answers,
        )
        self.app.database.questions.append(question)
        return question

    async def list_questions(
        self, theme_id: int | None = None
    ) -> list[Question]:
        if not theme_id:
            return self.app.database.questions

        questions = [
            question for question in self.app.database.questions if question.theme_id == theme_id
        ]
        return questions
