from django.urls import path
from questions import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/dislike/', views.dislike, name='question_dislike'),
    path('question/<int:question_id>/like/', views.question_like, name='question_like'),]
