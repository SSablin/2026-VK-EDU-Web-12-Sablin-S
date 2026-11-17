from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DefaultModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Question(DefaultModel):
    user = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=120, verbose_name="Заголовок вопроса")
    text = models.TextField(max_length=4095, verbose_name="Текст вопроса")


class Answer(DefaultModel):
    user = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.SET_NULL,
        null=True
    )
    question = models.ForeignKey(
        Question,
        verbose_name="Вопрос",
        on_delete=models.CASCADE
    )
    text = models.TextField(max_length=4095, verbose_name="Текст ответа")
    is_correct = models.BooleanField(verbose_name="Правильный ответ")


class Tag(DefaultModel):
    title = models.CharField(max_length=120, unique=True, verbose_name="Название тега")


class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "tag"],
                name="unique_question_tag"
            )
        ]


class QuestionLike(DefaultModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField(verbose_name="Лайк/дизлайк")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "user"],
                name="unique_question_like"
            )
        ]


class AnswerLike(DefaultModel):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField(verbose_name="Лайк/дизлайк")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["answer", "user"],
                name="unique_answer_like"
            )
        ]
