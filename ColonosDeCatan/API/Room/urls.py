from django.urls import path
from API.Room import views

urlpatterns = [
    path('rooms/', views.RoomCreateOrGet.as_view()),
    path('rooms/<int:pk>/', views.RoomJoinGetorDelete.as_view()),
]
