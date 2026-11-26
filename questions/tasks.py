import requests

from celery import shared_task
from django.conf import settings

from questions.models import Answer


@shared_task(bind=True, max_retries=3)
def publish_new_answer(self, answer_id):
    answer = Answer.objects.select_related('question', 'user').get(pk=answer_id)
    payload = {
        'channel': f"question:{answer.question_id}",
        'data': {
            'id': answer.id,
            'text': answer.text,
            'user': str(answer.user),
        },
    }

    try:
        response = requests.post(
            f"{settings.CENTRIFUGO_URL.rstrip('/')}/publish",
            json=payload,
            headers={'Authorization': f"apikey {settings.CENTRIFUGO_API_KEY}"},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=5)
