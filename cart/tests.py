from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from api.models import Menu, DiningTable, Order
from .views import cartadd, remove_item_from_order, checkout
from .cart import Cart
from django.test import TestCase, RequestFactory
from django.urls import reverse


def add_session_to_request(request):
    middleware = SessionMiddleware(lambda request: HttpResponse(""))
    middleware.process_request(request)
    request.session.save()

class CartTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.menu1 = Menu.objects.create(name="Pizza", price=9.99)  

    def test_add_to_cart(self):
        request = self.factory.post(reverse('cartadd'), {'menu_id': self.menu1.id, 'menuqty': 2})
        add_session_to_request(request) 
        response = cartadd(request)

    def test_checkout(self):
        request = self.factory.get(reverse('checkout'))
        add_session_to_request(request)

    def test_remove_item_from_cart(self):
        request = self.factory.post(reverse('remove_item_from_order', args=[self.menu1.id]))
        add_session_to_request(request)


class CartTestCase2(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.menu1 = Menu.objects.create(name="Pizza", price=9.99)  

    def test_add_to_cart(self):
        request = self.factory.post(reverse('cartadd'), {'menu_id': self.menu1.id, 'menuqty': 0})
        add_session_to_request(request) 
        response = cartadd(request)

    def test_checkout(self):
        request = self.factory.get(reverse('checkout'))
        add_session_to_request(request)

    def test_remove_item_from_cart(self):
        request = self.factory.post(reverse('remove_item_from_order', args=[self.menu1.id]))
        add_session_to_request(request)


