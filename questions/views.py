from django.shortcuts import render
from .utils import _make_questions, paginate


def index(request):
    questions = _make_questions()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    questions = sorted(_make_questions(), key=lambda q: q['rating'], reverse=True)
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag_name):
    questions = [q for q in _make_questions() if tag_name in q['tags']]
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/tag.html',
                  {'page': page, 'tag_name': tag_name})


def question(request, question_id):
    question_data = {
        'id': question_id,
        'title': f'Question {question_id}',
        'text': f'Text of question {question_id}',
        'author': 'Ivan Ivanov',
        'tags': ['html', 'learning'],
        'rating': 12,
    }
    answers = [
        {'id': i, 'text': f'answer {i}', 'author': 'Peter Petrov',
         'rating': i * 2, 'is_correct': i == 2}
        for i in range(1, 6)
    ]
    return render(request, 'questions/question.html',
                  {'question': question_data, 'answers': answers})


def ask(request):
    return render(request, 'questions/ask.html')
