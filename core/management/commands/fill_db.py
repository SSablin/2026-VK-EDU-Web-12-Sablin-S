from django.core.management import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from faker import Faker

from questions.models import (
    Tag, Question, Answer, QuestionTag,
    QuestionLike, AnswerLike,
)
from core.models import Profile

User = get_user_model()
fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "python manage.py fill_db [ratio]"

    def add_arguments(self, parser):
        parser.add_argument("ratio", nargs="?", type=int, default=1)

    @transaction.atomic
    def handle(self, *args, **options):
        if User.objects.exists():
            raise CommandError(
                "fill_db assumes an empty DB. Use a fresh DB or run `manage.py flush`."
            )
        ratio = options["ratio"]
        if ratio <= 0:
            raise CommandError("ratio must be positive integer number")

        batch_size = 50_000
        pwd_hash = make_password("password123")

        n_users = ratio
        n_questions = ratio * 10
        n_answers   = ratio * 100
        n_tags      = ratio

        n_qlikes = min(ratio * 100, n_users * n_questions)
        n_alikes = min(ratio * 100, n_users * n_answers)

        users_to_create = []
        for i in range(n_users):
            users_to_create.append(User(
                username=f"user_{i}",
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password=pwd_hash,
            ))
            if i != 0 and i % batch_size == 0:
                User.objects.bulk_create(users_to_create, batch_size=1_000)
                users_to_create.clear()
        if users_to_create:
            User.objects.bulk_create(users_to_create, batch_size=1_000)
            users_to_create.clear()

        profiles_to_create = []
        for i in range(n_users):
            profiles_to_create.append(Profile(
                user_id=i + 1,
                nickname=fake.user_name(),
            ))
            if i != 0 and i % batch_size == 0:
                Profile.objects.bulk_create(profiles_to_create, batch_size=1_000)
                profiles_to_create.clear()
        if profiles_to_create:
            Profile.objects.bulk_create(profiles_to_create, batch_size=1_000)
            profiles_to_create.clear()

        tags_to_create = []
        for i in range(n_tags):
            tags_to_create.append(Tag(title=f"tag_{i}_{fake.word()}"))
            if i != 0 and i % batch_size == 0:
                Tag.objects.bulk_create(tags_to_create, batch_size=1_000)
                tags_to_create.clear()
        if tags_to_create:
            Tag.objects.bulk_create(tags_to_create, batch_size=1_000)
            tags_to_create.clear()

        questions_to_create = []
        for i in range(n_questions):
            questions_to_create.append(Question(
                title=fake.sentence()[:120],
                text=fake.text(max_nb_chars=1000),
                user_id=(i % n_users) + 1,
            ))
            if i != 0 and i % batch_size == 0:
                Question.objects.bulk_create(questions_to_create, batch_size=1_000)
                questions_to_create.clear()
        if questions_to_create:
            Question.objects.bulk_create(questions_to_create, batch_size=1_000)
            questions_to_create.clear()

        question_tags_to_create = []
        for i in range(n_questions):
            question_tags_to_create.append(QuestionTag(
                question_id=i + 1,
                tag_id=(i % n_tags) + 1,
            ))
            if i != 0 and i % batch_size == 0:
                QuestionTag.objects.bulk_create(question_tags_to_create, batch_size=1_000)
                question_tags_to_create.clear()
        if question_tags_to_create:
            QuestionTag.objects.bulk_create(question_tags_to_create, batch_size=1_000)
            question_tags_to_create.clear()

        answers_to_create = []
        for i in range(n_answers):
            answers_to_create.append(Answer(
                question_id=(i % n_questions) + 1,
                user_id=(i % n_users) + 1,
                text=fake.text(max_nb_chars=500),
                is_correct=(i % 10 == 0),
            ))
            if i != 0 and i % batch_size == 0:
                Answer.objects.bulk_create(answers_to_create, batch_size=1_000)
                answers_to_create.clear()
        if answers_to_create:
            Answer.objects.bulk_create(answers_to_create, batch_size=1_000)
            answers_to_create.clear()

        question_likes_to_create = []
        for i in range(n_qlikes):
            user_idx = i % n_users
            question_idx = (i // n_users + user_idx) % n_questions
            question_likes_to_create.append(QuestionLike(
                user_id=user_idx + 1,
                question_id=question_idx + 1,
                is_like=(i % 2 == 0),
            ))
            if i != 0 and i % batch_size == 0:
                QuestionLike.objects.bulk_create(question_likes_to_create, batch_size=1_000)
                question_likes_to_create.clear()
        if question_likes_to_create:
            QuestionLike.objects.bulk_create(question_likes_to_create, batch_size=1_000)
            question_likes_to_create.clear()

        answer_likes_to_create = []
        for i in range(n_alikes):
            user_idx = i % n_users
            answer_idx = (i // n_users + user_idx) % n_answers
            answer_likes_to_create.append(AnswerLike(
                user_id=user_idx + 1,
                answer_id=answer_idx + 1,
                is_like=(i % 2 == 0),
            ))
            if i != 0 and i % batch_size == 0:
                AnswerLike.objects.bulk_create(answer_likes_to_create, batch_size=1_000)
                answer_likes_to_create.clear()
        if answer_likes_to_create:
            AnswerLike.objects.bulk_create(answer_likes_to_create, batch_size=1_000)
            answer_likes_to_create.clear()

        self.stdout.write(self.style.SUCCESS(
            f"Готово: users={n_users}, questions={n_questions}, answers={n_answers}, "
            f"tags={n_tags}, question_likes={n_qlikes}, answer_likes={n_alikes}"
        ))