from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, F, Q
from django.utils import timezone

from questions.models import Answer, Question, Tag

POPULAR_TAGS_CACHE_KEY = 'popular_tags_v1'
BEST_MEMBERS_CACHE_KEY = 'best_members_v1'

def paginate(objects_list, request, per_page=10):
    try:
        per_page = int(request.GET.get('per_page', per_page))
        if per_page <= 0 or per_page > 1000:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(objects_list, per_page)

    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def calculate_popular_tags(limit=10):
    since = timezone.now() - timedelta(days=90)
    recent_questions = Q(questiontag__question__created_at__gte=since)
    return list(
        Tag.objects
        .filter(questiontag__question__created_at__gte=since)
        .annotate(question_count=Count('questiontag', filter=recent_questions))
        .distinct()
        .order_by('-question_count', '-id')[:limit]
    )


def calculate_best_members(limit=10):
    since = timezone.now() - timedelta(days=7)
    scores = {}

    question_rows = (
        Question.objects
        .filter(created_at__gte=since, user_id__isnull=False)
        .annotate(
            likes=Count('questionlike', filter=Q(questionlike__is_like=True)),
            dislikes=Count('questionlike', filter=Q(questionlike__is_like=False)),
        )
        .annotate(rating=F('likes') - F('dislikes'))
        .values('user_id', 'rating')
    )
    for row in question_rows:
        scores[row['user_id']] = scores.get(row['user_id'], 0) + row['rating']

    answer_rows = (
        Answer.objects
        .filter(created_at__gte=since, user_id__isnull=False)
        .annotate(
            likes=Count('answerlike', filter=Q(answerlike__is_like=True)),
            dislikes=Count('answerlike', filter=Q(answerlike__is_like=False)),
        )
        .annotate(rating=F('likes') - F('dislikes'))
        .values('user_id', 'rating')
    )
    for row in answer_rows:
        scores[row['user_id']] = scores.get(row['user_id'], 0) + row['rating']

    ordered_ids = sorted(scores, key=lambda user_id: (-scores[user_id], -user_id))[:limit]
    if not ordered_ids:
        return []

    User = get_user_model()
    members_by_id = {
        member.id: member
        for member in User.objects.select_related('profile').filter(id__in=ordered_ids)
    }
    members = []
    for user_id in ordered_ids:
        member = members_by_id.get(user_id)
        if not member:
            continue
        best_question = (
            Question.objects
            .filter(user_id=user_id)
            .annotate(
                likes=Count('questionlike', filter=Q(questionlike__is_like=True)),
                dislikes=Count('questionlike', filter=Q(questionlike__is_like=False)),
            )
            .annotate(rating=F('likes') - F('dislikes'))
            .order_by('-rating', '-created_at', '-id')
            .first()
        )
        member.best_question_id = best_question.id if best_question else None
        members.append(member)
    return members