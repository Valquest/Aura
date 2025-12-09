from django.urls import path
from . import views


urlpatterns = [
    path('birthday', views.birthday_page, name='birthday_page'),
    path('api/birthday/', views.api_birthday_data, name='api_birthday'),
]