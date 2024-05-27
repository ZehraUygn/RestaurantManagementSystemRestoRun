"api/models.py"
from datetime import *
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    
    def to_dict(self):
        return {
            "username": self.username,
            "profile": self.profile.to_dict(),
        }


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    menu_item = models.ForeignKey('Menu', on_delete=models.CASCADE, null=True)
    stock = models.OneToOneField('Stock', on_delete=models.CASCADE, null=True, blank=True, related_name='ingredient_stock')

    def save(self, *args, **kwargs):
        is_new = self.pk is None  
        super().save(*args, **kwargs)
        if is_new and not self.stock:
            Stock.objects.create(ingredient=self, quantity=0)  

    def __str__(self):
        return self.name

class Stock(models.Model):
    ingredient = models.OneToOneField('Ingredient', on_delete=models.CASCADE, related_name='stock_ingredient')
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity}"
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='static/menu_images/', blank=True, default='static/menu_images/brik.png')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    ingredients = models.ManyToManyField(Ingredient)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='menu_items')

    def __str__(self):
        return self.name
    
class SurveyQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False) 

    def __str__(self):
        return self.question_text
    
class SurveyResponse(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.question.question_text} - {self.rating}"


class DiningTable(models.Model):
    STATUS_CHOICES = [            
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('asking bill', 'Asking Bill'),
    ]
    table_number = models.IntegerField(unique=True)
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Table {self.table_number} - {self.get_status_display()}"

    def update_status_based_on_order(self):
        if self.order_set.exists():
            self.status = 'occupied'
        else:
            self.status = 'available'
        self.save()

    class Meta:
        ordering = ['table_number']


class Order(models.Model):
    STATUS_CHOICES = [
        ('taken', 'Order Taken'),
        ('kitchen', 'Order In the Kitchen'),
        ('ready', 'Order Ready'),
        ('received', 'Order Received'),
        ('cancelled', 'Order Cancelled'),
        ('checkout', 'Checkout'),
    ]
    table = models.ForeignKey(DiningTable, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='taken')
    items = models.JSONField(default=dict)  
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} - Table: {self.table.table_number if self.table else 'N/A'}"
