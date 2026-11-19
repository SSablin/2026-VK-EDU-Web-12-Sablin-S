from django.urls import path
from questions import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/dislike/', views.question_dislike, name='question_dislike'),
    path('question/<int:question_id>/like/', views.question_like, name='question_like'),
    path('answer/<int:answer_id>/like/', views.answer_like, name='answer_like'),
    path('answer/<int:answer_id>/dislike/', views.answer_dislike, name='answer_dislike'),
    path('answer/<int:answer_id>/correct/', views.answer_correct, name='answer_correct'),
]
