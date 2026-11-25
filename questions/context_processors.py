from django.contrib.auth import get_user_model
from django.db.models import Count
from questions.models import Tag

User = get_user_model()


def popular_tags(request):
    return {'popular_tags': Tag.objects.popular()[:10]}

def best_members(request):
    members = (
        User.objects
        .select_related("profile")
        .annotate(answer_count=Count("answer"))
        .order_by("-answer_count", "-id")[:5]
    )
    return {"best_members": members}
