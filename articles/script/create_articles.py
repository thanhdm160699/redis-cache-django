import time
from django.utils.crypto import get_random_string

from articles.models import Article


def create_articles(num):
    articles = []
    start_time = time.time()
    for i in range(num):
        title = str(i+1) + get_random_string(50)
        content = str(i+1) + get_random_string(255)
        article = Article(title=title, content=content)
        articles.append(article)

        if len(articles) % 10000 == 0:
            Article.objects.bulk_create(articles)
            articles = []
            print(f"{i + 1} records inserted.")

    if articles:
        Article.objects.bulk_create(articles)

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")