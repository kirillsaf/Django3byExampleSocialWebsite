from django.urls import path
from . import views

urlpatterns = [
    # просмотры сообщений
    path('login/', views.user_login, name='login'),
]
