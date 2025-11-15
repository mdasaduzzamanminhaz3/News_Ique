from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from news.models import Category,Article,Review
from news.serializers import CategorySerializer,ArticleSerializer,ArticleWriteSerializer,ArticleDetailSerializer,ReviewSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser,AllowAny,IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings as main_settings
from drf_yasg.utils import swagger_auto_schema
from news.filters import ArticleFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from news.permissions import IsAdminOrEditor
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from users.models import User,SubscriptionPlan,Subscription
from users.serializers import SubscriptionPlanSerializer
from django.utils import timezone
from django.shortcuts import redirect,HttpResponseRedirect
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
        elif self.request.method in ["POST","PUT","PATCH"]:
            return [IsAdminOrEditor()]
        elif self.request.method == "DELETE":
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
        
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
    search_fields = ['headline', 'body', 'category__name']
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ArticleFilter
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        user = request.user
        is_article_premium = article.category.is_premium
        if is_article_premium:
            is_subscribed = False
            if user.is_authenticated:
                try:
                    user_subscription = user.subscription
                    is_subscribed = user_subscription.is_active
                except:
                    is_subscribed= False
            if not is_subscribed:
                paywall_data = {
                    "detail":"This article is premium. An active subscription is required to read the full article.",
                    "article_headline":article.headline,
                    "is_premium":True,
                    "teaser":article.body[:300] + "....",
                    "subscribe_url":"/api/v1/payment/initiate"
                }
                return Response(paywall_data,status=status.HTTP_403_FORBIDDEN)
        serializer= self.get_serializer(article)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def homepage(self, request):
        """
        Homepage endpoint: Featured article + paginated articles
        """
        qs = self.get_queryset().order_by("-published_at")

        # Featured article
        featured_article = qs.first()
        featured_data = None
        if featured_article:
            featured_data = ArticleDetailSerializer(featured_article).data

        # Paginate articles
        page = self.paginate_queryset(qs)
        articles_data = ArticleDetailSerializer(page, many=True).data if page else []

        return self.get_paginated_response({
            "featured": featured_data,
            "articles": articles_data
        })

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
            from_email=main_settings.EMAIL_HOST_USER,
            recipient_list=[self.request.user.email],
            fail_silently=True
        )

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list and retrieve Subscription Plans.
    Plans are public and read-only.
    """
    serializer_class=SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all().order_by('price_cents')
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    user = request.user
    user_id = user.id
    
    plan_id = request.data.get('plan_id')
    if not plan_id:
        return Response({"error":"Subscription plan ID is required"},status=status.HTTP_400_BAD_REQUEST)
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        amount = plan.price_cents
    except:
        return Response({"error":"Invalid subscription plan"}, status=status.HTTP_404_NOT_FOUND)
    tran_id = f"txn:{user.id}_{plan.id}_{int(timezone.now().timestamp())}"
    settings = { 'store_id': 'phima68e15b8a44795', 'store_pass': 'phima68e15b8a44795@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = tran_id
    post_body['success_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/success"
    post_body['fail_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/fail"
    post_body['cancel_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/cancel"
    post_body['emi_option'] = 0
    post_body['cus_name'] = f"{user.first_name} {user.last_name}"
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = "8978934"
    post_body['cus_add1'] = "None"
    post_body['cus_city'] = "Dhaka" 
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "News Subscription"
    post_body['product_category'] = "General"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body) # API response
    if response.get('status') == 'SUCCESS':
        return Response({'payment_url':response['GatewayPageURL']})
    return Response({"error":"payment initation failed"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def payment_success(request):
    tran_id = request.data.get('tran_id')
    if not tran_id:
        return Response({"error": "Transaction ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    txn_parts = tran_id.replace('txn:', '').split('_')
    if len(txn_parts) != 3:
        return Response({"error": "Invalid transaction ID"}, status=status.HTTP_400_BAD_REQUEST)
    
    user_id, plan_id, timestamp = txn_parts
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    plan = SubscriptionPlan.objects.get(id=plan_id)
    
    subscription, created = Subscription.objects.get_or_create(
        user=user,
        defaults={
            "plan": plan,
            "tran_id": tran_id,
            "started_at": timezone.now(),
            "ends_at": timezone.now() + timezone.timedelta(days=30),
            "is_active": True
        }
    )

    if not created:
        # Update existing subscription
        subscription.plan = plan
        subscription.tran_id = tran_id
        subscription.started_at = timezone.now()
        subscription.ends_at = timezone.now() + timezone.timedelta(days=30)
        subscription.is_active = True
        subscription.save()

    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/payment/success")
@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/subscription/plan")
@api_view(['POST'])
def payment_failed(request):
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/subscription/plan")
