from celery import shared_task
from cent import Client
from django.conf import settings
from django.core.cache import cache

from questions.utils import (
    BEST_MEMBERS_CACHE_KEY,
    POPULAR_TAGS_CACHE_KEY,
    calculate_best_members,
    calculate_popular_tags,
)


@shared_task(bind=True, max_retries=3)
def publish_new_answer(self, channel, data):
    try:
        client = Client(
            settings.CENTRIFUGO_API_URL,
            api_key=settings.CENTRIFUGO_API_KEY,
            request_timeout=5,
        )
        client.publish(channel=channel, data=data)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@shared_task
def update_popular_tags():
    tags = calculate_popular_tags()
    cache.set(POPULAR_TAGS_CACHE_KEY, [tag.id for tag in tags], timeout=60 * 30)
    return len(tags)


@shared_task
def update_best_members():
    members = calculate_best_members()
    cache.set(BEST_MEMBERS_CACHE_KEY, [member.id for member in members], timeout=60 * 30)
    return len(members)
