from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from news.models import Category,Article,Review
from news.serializers import CategorySerializer,ArticleSerializer,ArticleWriteSerializer,ArticleDetailSerializer,ReviewSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser,AllowAny
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]
       
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    # serializer_class=ArticleSerializer
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]
        
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def get_serializer_class(self):
        if self.action in ['list']:
            return ArticleSerializer
        elif self.action in ['retrieve']:
            return ArticleDetailSerializer
        elif self.action in ['create','update','partial_update']:
            return ArticleWriteSerializer
        else:
            return ArticleSerializer

class PublicArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class =ArticleDetailSerializer

    @action(detail=False,methods=['get'])
    def homepage(self,request):
        articles = self.get_queryset().order_by("-published_at")[:50]
        data = [
            {'headline':article.headline,
             'body':article.body[:50],
             'ratings':article.ratings,
              
            }

            for article in articles
        ]
        return Response(data)

class ReviewViewSet(viewsets.ModelViewSet):
    
    serializer_class = ReviewSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        article_id = (
            self.kwargs.get('article_pk') or self.kwargs.get('public_article_pk')
        )
        if article_id:
            return Review.objects.filter(article_id=article_id)
        return Review.objects.all()
    def perform_create(self, serializer):
        article_id = (
            self.kwargs.get('article_pk') or self.kwargs.get('public_article_pk')
        )
        review = serializer.save(user=self.request.user,article_id=article_id)
        article = Article.objects.filter(pk=article_id).first()
        headline = article.headline if article else 'Unknown Article'
        send_mail(
            subject = 'Thanks for your review',
            message=f"Hi {self.request.user.first_name},\n\n Thanks for your reviewing: {headline}.\nYour feedback means a lot!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.request.user.email],
            fail_silently=True
        )
