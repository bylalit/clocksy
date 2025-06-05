from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.FloatField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    image1 = models.ImageField(upload_to='product_image')
    image2 = models.ImageField(upload_to='product_image')
    image3 = models.ImageField(upload_to='product_image')
    def __str__(self):
        return self.name
    



