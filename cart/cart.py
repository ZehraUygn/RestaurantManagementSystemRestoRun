'cart/cart.py'
from api.models import Menu, Order, DiningTable
from cart.form import OrderForm


class Cart:


    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        self.cart = cart


    
    def db_add(self, menu, quantity):
	    
        menu_id = str(menu)
        menu_qty = str(quantity)
        if menu_id in self.cart:
            pass
        else:
            self.cart[menu_id] = int(menu_qty)
        self.session.modified = True

    def cart_total(self):
        menu_ids = self.cart.keys()
        menus = Menu.objects.filter(id__in=menu_ids)
        quantities = self.cart
        total = 0
        
        for key, value in quantities.items():
            key = int(key)
            for menu in menus:
                if menus.id == key:
                    total = total + (menu.price * value)
        return total
    
    def clear(self):
        self.session['session_key'] = {}
        self.session.modified = True
		

    def add(self, menu, quantity):
        menu_id = str(menu.id)
        menuqty= str(quantity)
        if menu_id in self.cart:
            pass
        else: 
            self.cart[menu_id] = int(menuqty)
        self.session.modified = True

    def __len__(self):
        return len(self.cart)
  
    def get_prods(self):
        menu_ids = self.cart.keys()
        menus = Menu.objects.filter(id__in=menu_ids)
        return menus
    

    def get_quants(self):
        return self.cart


    def update(self, menu_id, quantity):
        menu_id = str(menu_id)
        menu_qty = int(quantity)
        self.cart[menu_id] = menu_qty
        self.session.modified = True
    
    def save(self):
        self.session['session_key'] = self.cart
        self.session.modified = True


    def delete(self, menu):
        menu_id = str(menu)
        if menu_id in self.cart:
            del self.cart[menu_id]
        
        self.session.modified = True

    
    def checkout(request):
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                table_number = form.cleaned_data['table_number']
                note = form.cleaned_data['note']  

                cart = Cart(request)
                cart.checkout(table_number, note) 

                messages.success(request, "Order submitted successfully!")
                return redirect('some_success_url') 
            else:
                messages.error(request, "Error submitting the order. Please check your input.")
                return render(request, 'checkout.html', {'form': form})
        else:
            form = OrderForm()
            return render(request, 'checkout.html', {'form': form})


    def get_items(self):
        items = {}
        menu_ids = self.cart.keys()
        menus = Menu.objects.filter(id__in=menu_ids)
        for menu in menus:
            items[menu] = self.cart[str(menu.id)]
        return items


