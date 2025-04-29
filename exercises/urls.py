from django.urls import path
from . import views

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('exercise/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('exercise/<int:pk>/solved/', views.mark_exercise_solved, name='mark_exercise_solved'),
]