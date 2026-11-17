from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count, F, Q

from questions.managers import QuestionManager

User = get_user_model()


class DefaultModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Question(DefaultModel):
    objects = QuestionManager()
    user = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=120, verbose_name="Заголовок вопроса")
    text = models.TextField(max_length=4095, verbose_name="Текст вопроса")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
    def __str__(self):
        return f"Вопрос от {self.user} #{self.id}: {self.title}"

class AnswerManager(models.Manager):
    def for_question(self, question):
        return (
            self.get_queryset()
            .filter(question=question)
            .select_related("user")
            .annotate(
                likes=Count("answerlike", filter=Q(answerlike__is_like=True)),
                dislikes=Count("answerlike", filter=Q(answerlike__is_like=False)),
            )
            .annotate(rating=F("likes") - F("dislikes"))
            .order_by("-created_at")
        )


class Answer(DefaultModel):
    objects = AnswerManager()
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

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
    def __str__(self):
        return f"Ответ от {self.user} #{self.id} на вопрос #{self.question_id}"


class Tag(DefaultModel):
    title = models.CharField(max_length=120, unique=True, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class QuestionTag(models.Model):
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, verbose_name="Тег", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "tag"],
                name="unique_question_tag"
            )
        ]
        verbose_name = "Тег вопроса"
        verbose_name_plural = "Теги вопросов"


class QuestionLike(DefaultModel):
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    is_like = models.BooleanField(verbose_name="Лайк/дизлайк")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "user"],
                name="unique_question_like"
            )
        ]
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"


class AnswerLike(DefaultModel):
    answer = models.ForeignKey(Answer, verbose_name="Ответ", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    is_like = models.BooleanField(verbose_name="Лайк/дизлайк")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["answer", "user"],
                name="unique_answer_like"
            )
        ]
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"
