from django_filters import rest_framework as filters
from news.models import Article

class ArticleFilter(filters.FilterSet):
    category_id = filters.NumberFilter(field_name='category__id')
    category_name = filters.CharFilter(field_name='category__name',lookup_expr='icontains')
    last_news = filters.BooleanFilter(method='filter_last_news')

    class Meta:
        model = Article
        fields=['category_id','category_name','last_news']

    def filter_last_news(self,queryset,name,value):
        if value:
            return queryset.order_by('-published_at')
        return queryset