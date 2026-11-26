import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.db.models import Q, Case, When, Value, IntegerField
from django.contrib.postgres.search import SearchQuery, SearchRank
from questions.forms import AnswerForm, QuestionForm
from questions.models import Answer, Question, QuestionLike
from questions.tasks import publish_new_answer, send_answer_notification_email
from questions.utils import paginate
import re




def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request)
    return render(request, 'questions/index.html', {
        'page': page,
        'logined': request.user.is_authenticated,
    })


def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request)
    return render(request, 'questions/hot.html', {
        'page': page,
        'logined': request.user.is_authenticated,
    })


def tag(request, tag_name):
    page = paginate(Question.objects.by_tag(tag_name), request)
    return render(request, 'questions/tag.html',
                  {
                      'page': page,
                      'tag_name': tag_name,
                      'logined': request.user.is_authenticated,
                  })


import jwt
import time


@login_required(login_url='/login/')
def answer_fragment(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related('user', 'question'),
        pk=answer_id,
    )

    return render(request, 'questions/includes/answer_card.html', {
        'item': answer,
        'question': answer.question,
    })


def get_connection_token(user):
    subject = str(user.id) if user.is_authenticated else 'anonymous'
    return jwt.encode(
        {"sub": subject, "exp": int(time.time()) + 3600},
        settings.CENTRIFUGO_HMAC_SECRET,
        algorithm="HS256",
    )


def question(request, question_id):
    question_objects = get_object_or_404(Question.objects.with_related().with_rating(), pk=question_id)
    form = AnswerForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(
                f"{reverse('login')}?next={request.path}"
            )
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(request.user, question_objects)
            publish_new_answer.delay(
                f"question:{question_objects.id}",
                answer.as_json(),
            )
            send_answer_notification_email.delay(answer.id)
            return HttpResponseRedirect(
                f"{reverse('question', args=[question_objects.id])}#answer-{answer.id}"
            )

    page = paginate(Answer.objects.for_question(question_objects), request)
    return render(request, 'questions/question.html', {
        'question': question_objects,
        'page': page,
        'form': form,
        'logined': request.user.is_authenticated,
        'connection_token': get_connection_token(request.user),
        'centrifugo_channel': f'question:{question_objects.id}',
        'centrifugo_ws_url': settings.CENTRIFUGO_WS_URL,
        'is_first_answer_page': page.number == 1,
    })


def question_like(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    question_objects = get_object_or_404(Question.objects.with_related().with_rating(), pk=question_id)
    question_like, created = QuestionLike.objects.get_or_create(
        question=question_objects,
        user=request.user,
        defaults={'is_like': True},
    )
    if not created:
        if question_like.is_like:
            question_like.delete()
        else:
            question_like.is_like = True
            question_like.save()

    rating = QuestionLike.objects.filter(question=question_objects, is_like=True).count()
    rating -= QuestionLike.objects.filter(question=question_objects, is_like=False).count()
    current_like = QuestionLike.objects.filter(
        question=question_objects,
        user=request.user,
    ).values_list('is_like', flat=True).first()
    return JsonResponse({'rating': rating, 'is_like': current_like})


def question_dislike(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    question_objects = get_object_or_404(Question.objects.with_related().with_rating(), pk=question_id)
    question_like, created = QuestionLike.objects.get_or_create(
        question=question_objects,
        user=request.user,
        defaults={'is_like': False},
    )
    if not created:
        if question_like.is_like:
            question_like.is_like = False
            question_like.save()
        else:
            question_like.delete()

    rating = QuestionLike.objects.filter(question=question_objects, is_like=True).count()
    rating -= QuestionLike.objects.filter(question=question_objects, is_like=False).count()
    current_like = QuestionLike.objects.filter(
        question=question_objects,
        user=request.user,
    ).values_list('is_like', flat=True).first()
    return JsonResponse({'rating': rating, 'is_like': current_like})


def answer_like(request, answer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    answer = get_object_or_404(Answer.objects, pk=answer_id)
    try:
        like_type = json.loads(request.body).get('type')
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    if like_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid like type.'}, status=400)

    is_like = like_type == 'like'
    answer_like, created = answer.answerlike_set.get_or_create(
        answer=answer,
        user=request.user,
        defaults={'is_like': is_like},
    )
    if not created:
        if answer_like.is_like == is_like:
            answer_like.delete()
        else:
            answer_like.is_like = is_like
            answer_like.save()

    rating = answer.answerlike_set.filter(is_like=True).count()
    rating -= answer.answerlike_set.filter(is_like=False).count()
    current_like = answer.answerlike_set.filter(
        user=request.user,
    ).values_list('is_like', flat=True).first()
    return JsonResponse({'rating': rating, 'is_like': current_like})


def answer_dislike(request, answer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    answer = get_object_or_404(Answer.objects, pk=answer_id)
    try:
        like_type = json.loads(request.body).get('type')
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    if like_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid like type.'}, status=400)

    answer_like, created = answer.answerlike_set.get_or_create(
        answer=answer,
        user=request.user,
        defaults={'is_like': False},
    )
    if not created:
        if answer_like.is_like:
            answer_like.is_like = False
            answer_like.save()
        else:
            answer_like.delete()

    rating = answer.answerlike_set.filter(is_like=True).count()
    rating -= answer.answerlike_set.filter(is_like=False).count()
    current_like = answer.answerlike_set.filter(
        user=request.user,
    ).values_list('is_like', flat=True).first()
    return JsonResponse({'rating': rating, 'is_like': current_like})


def answer_correct(request, answer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    answer = get_object_or_404(Answer.objects, pk=answer_id)
    correct_type = request.POST.get('type')
    if request.body:
        try:
            correct_type = json.loads(request.body).get('type', correct_type)
        except (TypeError, json.JSONDecodeError):
            pass
    if correct_type not in ['correct', 'incorrect']:
        return JsonResponse({'error': 'Invalid correct type.'}, status=400)

    is_correct = correct_type == 'correct'
    question = answer.question
    if question.user != request.user:
        return JsonResponse({'error': 'Only the author of the question can mark an answer as correct.'}, status=403)

    if is_correct:
        Answer.objects.filter(question=question).update(is_correct=False)

    answer.is_correct = is_correct
    answer.save()

    return JsonResponse({'is_correct': answer.is_correct})


@login_required(login_url='/login/')
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(request.user)
            return HttpResponseRedirect(reverse('question', args=[question.id]))
    else:
        form = QuestionForm()
    return render(request, 'questions/ask.html', {
        'form': form,
        'logined': request.user.is_authenticated,
    })

def build_prefix_query(raw_query):
    # Оставляем только буквы, цифры и пробелы, чтобы не сломать raw-синтаксис PostgreSQL
    words = re.findall(r'\w+', raw_query)
    if not words:
        return None
    # Превращаем "python djan" в "python:* & djan:*"
    prefix_str = ' & '.join(f'{word}:*' for word in words)
    return SearchQuery(prefix_str, config='russian', search_type='raw')

def search(request):
    query = request.GET.get('q', '').strip()
    results = Question.objects.none()

    if query:
        search_query = build_prefix_query(query)
        if search_query:
            results = (
                Question.objects.filter(search_vector=search_query)
                .annotate(rank=SearchRank('search_vector', search_query))
                .order_by('-rank', '-created_at')
            )

    page = paginate(results, request)
    return render(request, 'questions/search.html', {
        'page': page,
        'query': query,
    })

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    search_query = build_prefix_query(query)
    if not search_query:
        return JsonResponse({'suggestions': []})

    questions = (
        Question.objects.filter(search_vector=search_query)
        .annotate(rank=SearchRank('search_vector', search_query))
        .order_by('-rank')[:5]
    )

    suggestions = [
        {
            'id': q.id,
            'title': q.title,
            # Если маршрут вопроса называется иначе, замените 'question' на ваше имя из urls.py
            'url': reverse('question', args=[q.id]),
        }
        for q in questions
    ]
    return JsonResponse({'suggestions': suggestions})
