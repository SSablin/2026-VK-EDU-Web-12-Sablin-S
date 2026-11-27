from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Question

@receiver(post_save, sender=Question)
def update_search_vector(sender, instance, **kwargs):
    Question.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector('title', weight='A', config='russian') +
            SearchVector('text', weight='B', config='russian')
        )
    )
