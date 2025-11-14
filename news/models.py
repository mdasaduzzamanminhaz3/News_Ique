from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=250,blank=True,null=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)    
    
    def __str__(self):
        return self.name


class Article(models.Model):
    headline = models.CharField(max_length=300)
    body = models.TextField()
    # image = models.ImageField(upload_to='article/',blank=True,null=True)
    image =CloudinaryField('article_image' ,default='placeholder', blank=True, null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    published_at = models.DateTimeField(blank=True,null=True)
    is_published= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def publish(self):
        self.is_published = True

        if not self.published_at:
            self.published_at = timezone.now()
        self.save()
    def __str__(self):
        return self.headline

class Review(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ratings = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(4)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.first_name} on {self.article.headline}"