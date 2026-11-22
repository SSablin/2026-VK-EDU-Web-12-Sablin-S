from django.db import models
from django.db.models import Count, F, Q


class QuestionQuerySet(models.QuerySet):
    def with_related(self):
        return self.select_related("user").prefetch_related("questiontag_set__tag")

    def with_rating(self):
        return self.annotate(
            likes=Count("questionlike", filter=Q(questionlike__is_like=True)),
            dislikes=Count("questionlike", filter=Q(questionlike__is_like=False)),
        ).annotate(rating=F("likes") - F("dislikes"))


class QuestionManager(models.Manager.from_queryset(QuestionQuerySet)):
    def new(self):
        return self.get_queryset().with_related().with_rating().order_by("-created_at")

    def best(self):
        return self.get_queryset().with_related().with_rating().order_by("-rating", "-created_at")

    def by_tag(self, tag_name):
        return (
            self.get_queryset()
            .filter(questiontag__tag__title=tag_name)
            .with_related()
            .with_rating()
            .order_by("-created_at")
        )
