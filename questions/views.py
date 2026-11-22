from django.shortcuts import render, get_object_or_404
from questions.models import Answer, Question
from questions.utils import paginate


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request)
    return render(request, 'questions/index.html', {'page': page, 'logined': False})


def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request)
    return render(request, 'questions/hot.html', {'page': page, 'logined': False})


def tag(request, tag_name):
    page = paginate(Question.objects.by_tag(tag_name), request)
    return render(request, 'questions/tag.html',
                  {'page': page, 'tag_name': tag_name, 'logined': False})


def question(request, question_id):
    question = get_object_or_404(Question.objects.with_related().with_rating(), pk=question_id)
    page = paginate(Answer.objects.for_question(question), request)
    return render(request, 'questions/question.html', {'question': question, 'page': page, 'logined': False})


def ask(request):
    return render(request, 'questions/ask.html', {'logined': True})
