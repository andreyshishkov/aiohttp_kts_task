from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import request_schema, response_schema

from app.quiz.schemes import ThemeSchema, QuestionSchema
from app.quiz.models import Answer
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(AuthRequiredMixin, View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем


    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title =   self.data['title']
        # TODO: заменить на self.data["title"] после внедрения валидации
        # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(
            data={'themes': [ThemeSchema().dump(theme) for theme in themes]}
        )


class QuestionAddView(AuthRequiredMixin, View):

    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data.get('title')
        theme_id = self.data.get('theme_id')
        answers = self.data.get('answers')

        if len(answers) == 1:
            raise HTTPBadRequest(text='It must be at least 2 answers')

        if sum(answer['is_correct'] for answer in answers) != 1:
            raise HTTPBadRequest(text='Number of right answers is exactly one')

        if not await self.store.quizzes.get_theme_by_id(theme_id):
            raise HTTPNotFound(text='Theme is not founded')

        if await self.store.quizzes.get_question_by_title(title):
            raise HTTPConflict(text='There is already question with that title')

        question = await self.store.quizzes.create_question(
            title=title, theme_id=theme_id, answers=[
                Answer(
                    title=answer["title"],
                    is_correct=answer["is_correct"]
                ) for answer in answers
            ])
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):

    @response_schema(QuestionSchema)
    async def get(self):
        theme_id = None
        if self.request.query:
            theme_id = self.request.query.get('theme_id')

        if not theme_id:
            questions = await self.store.quizzes.list_questions()
            questions_dict = [QuestionSchema().dump(question) for question in questions]
            return json_response(
                data={
                    "questions": questions_dict,
                }
            )

        theme_questions = await self.store.quizzes.list_questions(theme_id)
        questions_dict = [QuestionSchema().dump(question) for question in theme_questions]
        return json_response(
            data={
                "questions": questions_dict,
            }
        )