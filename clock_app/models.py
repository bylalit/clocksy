from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_image/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='brand_image/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    STOCK_STATUS = (
        ('In Stock', 'In Stock'),
        ('Out of Stock', 'Out of Stock'),
    )

    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products'
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField()

    image1 = models.ImageField(upload_to='product_image/')
    image2 = models.ImageField(upload_to='product_image/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_image/', blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)

    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_STATUS,
        default='In Stock'
    )

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    

class Order(models.Model):

    STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
    
class OrderItem(models.Model):

    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='items')

    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10,
                                decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product.name
    