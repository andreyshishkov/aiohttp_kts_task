from app.quiz.schemes import ThemeSchema, ThemeListSchema, QuestionSchema, ListQuestionSchema, ThemeIdSchema
from app.web.app import View
from app.web.utils import json_response
from app.web.mixins import AuthRequiredMixin
from aiohttp_apispec import request_schema, response_schema, querystring_schema
from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound

# TODO: добавить проверку авторизации для этого View
class ThemeAddView(AuthRequiredMixin, View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    async def post(self):
        title = self.data["title"]

        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            raise HTTPConflict(reason="Theme with this title already exists")

        # TODO: заменить на self.data["title"] после внедрения валидации
        # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))

class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema, 200)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = self.data["answers"]

        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            raise HTTPNotFound(reason="Theme not found")

        existing_question = await self.store.quizzes.get_question_by_title(title)
        if existing_question:
            raise HTTPConflict(reason="Question with this title already exists")

        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=answers
        )

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema, 200)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        if theme_id:
            theme_id = int(theme_id)

        questions = await self.store.quizzes.list_questions(theme_id)
        return json_response(data=ListQuestionSchema().dump({"questions": questions}))
