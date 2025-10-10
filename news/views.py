from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from news.models import Category,Article,Review
from news.serializers import CategorySerializer,ArticleSerializer,ArticleWriteSerializer,ArticleDetailSerializer,ReviewSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser,AllowAny
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import FilterSet
from news.filters import ArticleFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Manage article categories.

    This viewset allows:
    -  Public access to view all categories (`GET`)
    -  Admin-only access to create, update, or delete categories (`POST`, `PUT`, `PATCH`, `DELETE`)

    Categories help organize articles and support filtering by topic or section.

    Permissions:
    - `GET`: Open to all users
    - Other methods: Restricted to admin users

    Example Endpoints:
    - GET /api/categories/
    - POST /api/categories/  (admin only)
    - PUT /api/categories/{id}/  (admin only)

    Responses:
    - 200 OK: List or detail of categories
    - 201 Created: New category added
    - 403 Forbidden: Unauthorized access
    - 404 Not Found: Invalid category ID
    """

    pagination_class=PageNumberPagination
    search_fields = ['category__name','category_id']
    filter_backends=[DjangoFilterBackend,SearchFilter]  

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]
    
class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing news articles.

    This viewset supports the following operations:
    - List all articles
    - Retrieve a single article by ID
    - Create a new article
    - Update an existing article
    - Delete an article

    Filtering and search options:
    - Filter by category, author, or publication date
    - Search by title or content keywords

    Permissions:
    - Authenticated Editor can create and update articles
    - Only admins can delete articles

    Responses:
    - 200 OK: Successful retrieval
    - 201 Created: Article successfully created
    - 400 Bad Request: Validation errors
    - 403 Forbidden: Permission denied
    - 404 Not Found: Article not found
    """
    pagination_class=PageNumberPagination
 
    queryset = Article.objects.all()
    filterset_class = ArticleFilter
    search_fields = ['headline', 'body','category__name']


    filter_backends=[DjangoFilterBackend,SearchFilter]  
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
    @swagger_auto_schema(
            operation_summary ="Retrieve a list of  articles"
    )
    def list(self, request, *args, **kwargs):
        """ Retrive all the article"""
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
            operation_summary ="Create an article by editor"
    )
    def create(self, request, *args, **kwargs):
        """ Only Editor can Create an article """
        return super().create(request, *args, **kwargs)
    


class PublicArticleViewSet(viewsets.ReadOnlyModelViewSet):
    search_fields = ['headline', 'body','category__name']
    pagination_class=PageNumberPagination

    filter_backends=[DjangoFilterBackend,SearchFilter]  
    filterset_class = ArticleFilter  
    queryset = Article.objects.filter(is_published=True)
    serializer_class =ArticleDetailSerializer

    @action(detail=False,methods=['get'])
    def homepage(self,request):
        """
    Retrieve the latest published articles for homepage display.

    This endpoint returns a simplified list of up to 50 recently published articles,
    ordered by `published_at` in descending order. Each article includes:
    - `headline`: Title of the article
    - `body`: First 50 characters of the article body
    - `ratings`: Average rating or score (if available)

    This is optimized for homepage previews, not full article details.

    Responses:
    - 200 OK: Returns a list of article previews
    - 500 Internal Server Error: Unexpected failure

    Example:
    GET /api/public-articles/homepage/
    """

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
    
    """
    This endpoint allows authenticated users to post a review on an article.
    Reviews typically include:
    - `rating`: Integer value (e.g., 1-4)
    - `reviewer`: Auto-assigned from the authenticated user

    """
    @swagger_auto_schema(
            operation_summary='only authenticated user can create a review'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
            operation_summary='only editor or admin  can retrive a single review'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
            operation_summary='only authenticated itself user can delete a review'
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
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
        article = Article.objects.filter(pk=article_id).first()
        review = serializer.save(user=self.request.user, article=article)
        headline = article.headline if article else 'Unknown Article'
        send_mail(
            subject = 'Thanks for your review',
            message=f"Hi {self.request.user.first_name},\n\n Thanks for your reviewing: {headline}.\nYour feedback means a lot!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.request.user.email],
            fail_silently=True
        )
