"""URL configuration for blog app."""
from django.urls import path, include
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('categories/', views.CategoriesView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryListView.as_view(), name='category'),
    path('tags/', views.TagsView.as_view(), name='tag_list'),
    path('tags/<slug:slug>/', views.TagListView.as_view(), name='tag'),
    path('archives/', views.ArchivesView.as_view(), name='archives'),
    path('about/', views.about, name='about'),
    path('links/', views.links, name='links'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('search/', views.search, name='search'),
    path('contact/', include('contact.urls')),
    path('pages/', include('pages.urls')),
]
