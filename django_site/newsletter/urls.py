from django.urls import path

from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('resources/<slug>/', views.lead_magnet, name='lead_magnet'),
    path('api/subscribers/', views.subscribers_api, name='subscribers_api'),
    path('export.csv', views.export_csv, name='export_csv'),
]
