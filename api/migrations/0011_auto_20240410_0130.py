from django.db import migrations

def create_stocks_for_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('api', 'Ingredient')
    Stock = apps.get_model('api', 'Stock')
    for ingredient in Ingredient.objects.all():
        Stock.objects.get_or_create(ingredient=ingredient, defaults={'quantity': 0})

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0010_remove_diningtable_is_occupied_diningtable_status'),  # Replace with the correct dependency
    ]

    operations = [
        migrations.RunPython(create_stocks_for_ingredients),
    ]
