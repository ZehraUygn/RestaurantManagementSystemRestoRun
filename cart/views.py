'cart/views.py'
from django.shortcuts import render, get_object_or_404

from api import models
from .cart import Cart
from api.models import Menu
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from api.models import DiningTable, Order

from .form import OrderForm
from .cart import Cart


def cartsum(request):
    cart = Cart(request)
    cartitems = cart.get_prods()
    quantities = cart.get_quants()
    total_price = sum(item.price * quantities.get(str(item.id), 0) for item in cartitems)
    return render(request, "cartsum.html", {"cartitems": cartitems, "quantities": quantities, "total_price": total_price})

def cartadd(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        menu_id = int(request.POST.get('menu_id'))
        menu_qty = request.POST.get('menuqty')
        if menu_qty is None:
            return JsonResponse({'error': 'Quantity parameter missing'}, status=400)
        menu_qty = int(menu_qty)
        menu = get_object_or_404(Menu, id=menu_id)
        cart.add(menu=menu, quantity=menu_qty)

        cartquantity = cart.__len__()

        response = JsonResponse({'qty': cartquantity})
        return response


def remove_item_from_order(request, item_id):
    if request.method == 'POST':
        cart = Cart(request)
        cart.delete(menu=item_id)  

        messages.success(request, "Item removed successfully.")
        return redirect('checkout') 

def checkout(request):
    tables = DiningTable.objects.all()
    cart = Cart(request)
    order_items = cart.get_items()  
    total_price = sum(item.price * quantity for item, quantity in order_items.items())
    return render(request, "checkout.html", {
        "tables": tables,
        "order_items": order_items,
        "total_price": total_price  
    })

def submit_order(request):
    print("Button Pressed")
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            table_id = form.cleaned_data['table_number']
            order_note = form.cleaned_data.get('note', '')

            table = get_object_or_404(DiningTable, id=table_id)
            cart = Cart(request)
            items_json = {str(item.id): quantity for item, quantity in cart.get_items().items()}
            total_price = sum(item.price * quantity for item, quantity in cart.get_items().items())
            print("Button Pressed")
            order = Order.objects.create(
                table=table,
                items=items_json,
                total_price=total_price,
                note= order_note 
            )
            
            cart.clear()
            messages.success(request, "Order submitted successfully!")
            return redirect('api:survey')  
        else:
            messages.error(request, "Error submitting the order. Please check your input.")
            return render(request, 'checkout.html', {'form': form})

    return redirect('/cart/')
