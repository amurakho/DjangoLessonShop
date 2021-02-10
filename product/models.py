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


class ProductInBucket(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)


class Bucket(models.Model):
    full_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    products_in_bucket = models.ManyToManyField(ProductInBucket)
    full_count = models.IntegerField(default=0)

    def update_price(self):
        price = 0
        count = 0

        for product_in_bucket in self.products_in_bucket.all():
            price += product_in_bucket.count * product_in_bucket.product.price
            count += product_in_bucket.count

        self.full_count = count
        self.full_price = price
