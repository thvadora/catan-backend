from django.urls import path
from API.PlayerInfo import views

urlpatterns = [
    path('games/<int:id>/player',
         views.PlayerPersonalInfo.as_view()),
]
