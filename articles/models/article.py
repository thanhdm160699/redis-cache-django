from django.db import models

from redis_cache_django.base_common.base_cache_mixin import BaseCacheMixin


class Article(models.Model, BaseCacheMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
