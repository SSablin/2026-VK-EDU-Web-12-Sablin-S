from celery import shared_task
from cent import Client
from django.conf import settings


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
