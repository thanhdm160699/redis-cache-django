from rest_framework import serializers

from redis_cache_django.articles.models.article import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'