"api\admin.py"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Menu, Ingredient, Order, Stock, DiningTable, Category

admin.site.register(User, UserAdmin)
admin.site.register(Ingredient)
admin.site.register(Stock) 
admin.site.register(Order) 
admin.site.register(DiningTable)
admin.site.register(Category)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1

class MenuAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]

admin.site.register(Menu, MenuAdmin)


