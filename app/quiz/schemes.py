from marshmallow import Schema, fields, pre_load, ValidationError
from marshmallow.fields import Nested, Int

class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True, required=True)

    @pre_load
    def validate_answers(self, data, **kwargs):
        answers = data.get("answers", [])

        if len(answers) < 2:
            raise ValidationError("Question must have at least 2 answers")

        correct_count = sum(1 for a in answers if a.get("is_correct"))
        if correct_count == 0:
            raise ValidationError("Question must have at least one correct answer")
        if correct_count > 1:
            raise ValidationError("Question must have exactly one correct answer")

        return data

class ThemeListSchema(Schema):
    themes = Nested(ThemeSchema, many=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int(required=False, allow_none=True)

class ListQuestionSchema(Schema):
    questions = Nested(QuestionSchema, many=True, only=["id", "title", "theme_id", "answers"])
