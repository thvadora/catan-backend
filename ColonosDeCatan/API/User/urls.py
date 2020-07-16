from django.urls import path
from API.User import views

urlpatterns = [
    path('users/', views.RegisterUser.as_view()),
    path('users/login/', views.CustomAuthToken.as_view()),
]
