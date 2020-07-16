from django.urls import path
from API.Games import views

urlpatterns = [
    path('games/<int:id>/board', views.boardStatus.as_view()),
    path('games/<int:pk>/player/actions', views.PlayAction.as_view()),
    path('games/<int:pk>', views.GetGame.as_view()),
    path('games/', views.ListGames.as_view()),

]
