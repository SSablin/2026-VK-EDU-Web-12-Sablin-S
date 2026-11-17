from django.db import models
from django.db.models import Q, Count


class QuestionManager(models.Manager):
    def new(self):
        return self.get_queryset().order_by('-created_at')

    def best(self):
        return self.get_queryset().annotate(
            rating=Count('questionlike', filter=Q(questionlike__is_like=True))).order_by('-rating', '-created_at')
