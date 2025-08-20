from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from news.views import *

router = DefaultRouter()
router.register('categories',CategoryViewSet,basename='category')
router.register('articles',ArticleViewSet,basename='article')
router.register('reviews',ReviewViewSet,basename='review')
router.register('public_articles',PublicArticleViewSet,basename='public_articles')

articles_router = routers.NestedDefaultRouter(router,'articles',lookup='article')
articles_router.register('reviews',ReviewViewSet,basename='article-review')

public_article_router = routers.NestedDefaultRouter(router,'public_articles',lookup='public_article')
public_article_router.register('reviews',ReviewViewSet,basename='public-article-review')

urlpatterns = [
    path('',include(router.urls)),
    path('',include(articles_router.urls)),
    path('',include(public_article_router.urls)),
    
]

