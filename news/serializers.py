from rest_framework import serializers
from .models import Category,Article,Review
from django.utils import timezone
from users.serializers import CurrentUserSerializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =['id','name','description']

class ArticleSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(read_only=True)
    category = serializers.HyperlinkedRelatedField(
        queryset = Category.objects.all(),
        view_name ='category-detail'
    )
    image = serializers.SerializerMethodField() 
    class Meta:
        model = Article
        fields =['id','category','headline','image','body','published_at','author']
        
    def get_image(self, obj):
        if obj.image and obj.image.url != "placeholder":
            return obj.image.url
        return None

    
class ReviewSerializer(serializers.ModelSerializer):
    article_headline = serializers.SerializerMethodField()
    user = CurrentUserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id','article_headline','comment','ratings','created_at','user']
    def get_article_headline(self,obj):
        return getattr(obj.article,'headline',None)

class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image=serializers.ImageField()

    rating = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = ["id", "headline",'image',"body", "category", "rating", "published_at"]

    def get_rating(self,obj):
        reviews = obj.reviews.all()

        if reviews.exists():
            return round(sum([r.ratings for r in reviews]))
        return None

class ArticleWriteSerializer(serializers.ModelSerializer):
    image=serializers.ImageField()

    class Meta:
        model = Article
        fields = ["id","headline",'image', "body", "category", "is_published","published_at"]
        read_only_fields =['id',"published_at"]
        
    def create(self, validated_data):
        if validated_data.get("is_published") and not validated_data.get("published_at"):
            validated_data['published_at'] = timezone.now()
        return super().create(validated_data)
    
    def update(self,instance,validated_data):
        if validated_data.get("is_published") and not instance.published_at:
            instance.published_at = timezone.now()
        return super().update(instance,validated_data)

