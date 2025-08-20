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
        fields = ['id','article','article_headline','ratings']
    def get_article_headline(self,obj):
        view = self.context.get('view')
        article_id = view.kwargs.get('article_pk') or view.kwargs.get('public_article_pk')
        if article_id:
            try:
                return Article.objects.get(pk=article_id).headline
            except Article.DoesNotExist:
                return None
        return None

class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
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
    class Meta:
        model = Article
        fields = ["headline",'image', "body", "category", "is_published"]

