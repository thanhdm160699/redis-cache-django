from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from articles.models import Article
from articles.serializers.article import ArticleSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def list(self, request, *args, **kwargs):
        ids = []
        for i in range(int(request.query_params.get("from")), int(request.query_params.get("to"))):
            ids.append(i)
        articles = Article.load_multiple(instance_ids=ids)
        return Response(data=articles)

    def retrieve(self, request, *args, **kwargs):
        article = Article.load(kwargs.get("pk"))
        serializer = self.serializer_class(article)
        return Response(serializer.data)
