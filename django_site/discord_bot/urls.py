from django.urls import path

from . import views

app_name = 'discord_bot'

urlpatterns = [
    path('interactions/', views.discord_interactions, name='interactions'),
]
