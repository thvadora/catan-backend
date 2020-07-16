from django.urls import path
from API.Board import views

urlpatterns = [
    path('boards', views.boardList.as_view()),
]
