from django.urls import path

from . import views

app_name = 'content_pipeline'

urlpatterns = [
    path('curate/', views.scheduler_curate, name='scheduler_curate'),
    path('check-content/', views.scheduler_check_content, name='scheduler_check_content'),
]
