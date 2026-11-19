from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from questions.forms import AnswerForm
from questions.models import Answer, Question, QuestionLike
from questions.utils import paginate


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
            return HttpResponseRedirect(
                f"{reverse('question', args=[question_objects.id])}#answer-{answer.id}"
            )

    page = paginate(Answer.objects.for_question(question_objects), request)
    return render(request, 'questions/question.html', {
        'question': question_objects,
        'page': page,
        'form': form,
        'logined': request.user.is_authenticated,
    })

@login_required(login_url='/login/')
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
    return JsonResponse({'rating': rating})

def dislike(request, question_id):
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
    return JsonResponse({'rating': rating})

@login_required(login_url='/login/')
def ask(request):
    return render(request, 'questions/ask.html', {
        'logined': request.user.is_authenticated,
    })
