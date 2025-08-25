from rest_framework import serializers
from .models import Category,Article,Review

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
    
    class Meta:
        model = Article
        fields =['id','category','headline','image','body','published_at','author']


    
class ReviewSerializer(serializers.ModelSerializer):
    article_headline = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id','article_headline','comment','ratings']
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
        fields = ["headline",'image', "body", "category", "is_published"]

