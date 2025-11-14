from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from users.views import UserListView
from news.views import CategoryViewSet,ArticleViewSet,ReviewViewSet,PublicArticleViewSet,SubscriptionPlanViewSet,initiate_payment,payment_success,payment_cancel,payment_failed

router = DefaultRouter()
router.register('categories',CategoryViewSet,basename='category')
router.register('articles',ArticleViewSet,basename='article')
router.register('reviews',ReviewViewSet,basename='review')
router.register('public_articles',PublicArticleViewSet,basename='public_articles')
router.register('users_list',UserListView,basename='user')
router.register('subscriptions_plans',SubscriptionPlanViewSet,basename="subscription-plan")
articles_router = routers.NestedDefaultRouter(router,'articles',lookup='article')
articles_router.register('reviews',ReviewViewSet,basename='article-review')

public_article_router = routers.NestedDefaultRouter(router,'public_articles',lookup='public_article')
public_article_router.register('reviews',ReviewViewSet,basename='public-article-review')

urlpatterns = [
    path('',include(router.urls)),
    path('',include(articles_router.urls)),
    path('',include(public_article_router.urls)),
    path('payment/initiate',initiate_payment,name='initiate-payment'),
    path('payment/success',payment_success,name='payment-success'),
    path('payment/fail',payment_failed,name='payment-failed'),
    path('payment/cancel',payment_cancel,name='payment-cancel')
]

