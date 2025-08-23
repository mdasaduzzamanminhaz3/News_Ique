from django.contrib import admin
from news.models import * 
# Register your models here.
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Review)