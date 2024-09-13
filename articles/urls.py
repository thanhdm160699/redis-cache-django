# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles.views.articles_view import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='articles')

urlpatterns = [
    path('', include(router.urls)),
]