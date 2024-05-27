from django.test import TestCase
from django.urls import reverse
from .models import User, Menu, Ingredient, Category
from .forms import LoginForm, MenuForm
from django.test import TestCase, Client
from django.urls import reverse
from .models import User
from django.core.exceptions import ValidationError
from .models import Menu, Category, Ingredient


class MenuViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name="Starters")
        self.ingredient = Ingredient.objects.create(name="Tomato")
        self.menu = Menu.objects.create(
            name="Tomato Soup",
            category=self.category,
            price=9.99  
        )
        self.menu.ingredients.add(self.ingredient)

    def test_list_menu_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('api:listeM'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomato Soup")

    def test_create_menu_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('api:create'), {
            'name': 'New Dish',
            'category': self.category.id,
            'ingredients': [self.ingredient.id],
            'price': 15.00 
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Menu.objects.filter(name='New Dish').exists())


class LoginFormTests(TestCase):
    def test_form_valid(self):
        form_data = {'username': 'testuser', 'password': '12345'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {'username': '', 'password': ''}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class AccessControlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_access_restricted_pages_with_login(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('api:listeM'))
        self.assertEqual(response.status_code, 200)
