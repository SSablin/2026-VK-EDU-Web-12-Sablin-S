from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from questions.forms import AnswerForm
from questions.models import Answer, Question
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
    question = get_object_or_404(Question.objects.with_related().with_rating(), pk=question_id)
    form = AnswerForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(
                f"{reverse('login')}?next={request.path}"
            )
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(request.user, question)
            return HttpResponseRedirect(
                f"{reverse('question', args=[question.id])}#answer-{answer.id}"
            )

    page = paginate(Answer.objects.for_question(question), request)
    return render(request, 'questions/question.html', {
        'question': question,
        'page': page,
        'form': form,
        'logined': request.user.is_authenticated,
    })


@login_required(login_url='/login/')
def ask(request):
    return render(request, 'questions/ask.html', {
        'logined': request.user.is_authenticated,
    })
