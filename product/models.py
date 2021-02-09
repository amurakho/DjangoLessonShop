from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.contrib.auth.models import User
from product.utils import my_slugify


class Category(models.Model):
    slug = AutoSlugField(populate_from='name', slugify_function=my_slugify)
    name = models.CharField(max_length=100)


class Product(models.Model):
    slug = AutoSlugField(populate_from='title', slugify_function=my_slugify)
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='images')
    created_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=3)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(default=3)

