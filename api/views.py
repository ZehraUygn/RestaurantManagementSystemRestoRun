"api/views.py"
from time import timezone
from django.http import HttpResponse, HttpRequest, JsonResponse,Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.http.multipartparser import MultiPartParser
from django.urls import reverse
from .models import User
from .forms import  LoginForm
from django.contrib import auth, messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.http import QueryDict
from django.views.decorators.http import require_http_methods
from .models import Menu, Ingredient, Stock, Order
from .forms import MenuForm, OrderForm
from django.contrib.auth.decorators import login_required
from .models import DiningTable, Category, SurveyQuestion, SurveyResponse
from .forms import CategoryForm, IngredientForm, SurveyQuestionForm, SurveyResponseForm
from django.views.decorators.http import require_POST
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime
import logging
from django.db.models import Min
from django.db.models import Sum, Q
from django.utils.timezone import localdate
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncMonth



@login_required
def manage_survey(request):
    if request.method == 'POST':
        form = SurveyQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('api:manage_survey')
    else:
        form = SurveyQuestionForm()
    questions = SurveyQuestion.objects.filter(active=True)
    return render(request, 'api/spa/manage_survey.html', {'form': form, 'questions': questions})

def survey(request):
    questions = SurveyQuestion.objects.filter(active=True)
    if request.method == 'POST':
        responses = []
        for question in questions:
            response = SurveyResponse(
                question=question,
                rating=request.POST.get(f'rating_{question.id}'),
                comment=request.POST.get(f'comment_{question.id}', '')
            )
            responses.append(response)
        SurveyResponse.objects.bulk_create(responses)
        return redirect('api:survey_thank_you')  
    return render(request, 'api/spa/survey.html', {'questions': questions})

def survey_thank_you(request):
    return render(request, 'api/spa/survey_thank_you.html')


@login_required
def delete_survey_question(request, question_id):
    question = get_object_or_404(SurveyQuestion, pk=question_id)
    question.is_deleted = True 
    question.active = False
    question.save()
    return redirect('api:manage_survey')

@login_required
def view_responses(request):
    sort = request.GET.get('sort', 'newest') 

    if sort == 'highest':
        responses = SurveyResponse.objects.order_by('-rating')
    elif sort == 'lowest':
        responses = SurveyResponse.objects.order_by('rating')
    elif sort == 'oldest':
        responses = SurveyResponse.objects.order_by('id')
    else:  # 'newest'
        responses = SurveyResponse.objects.order_by('-id')

    return render(request, 'api/spa/view_responses.html', {'responses': responses, 'sort': sort})

@csrf_exempt
def loginPage(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("/listeM/")
            else:
                messages.error(request, "Invalid login details.")
        else:
            messages.error(request, "Invalid form details.")
    return render(request, "api/spa/login.html", {"form": form})


def logout(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
    else:
        auth.logout(request)
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))


@login_required
def create(request):
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.save()
            ingredients = request.POST.getlist('ingredients')     
            new_ingredient_name = request.POST.get('newIngredient', '').strip()
            if new_ingredient_name:
                new_ingredient = Ingredient.objects.create(name=new_ingredient_name)
                ingredients.append(new_ingredient.id)  
            menu.ingredients.set(ingredients)
            return redirect('api:listeM')
    else:
        form = MenuForm()
        ingredients = Ingredient.objects.all()  
    return render(request, 'api/spa/create.html', {'form': form, 'ingredients': ingredients})


@login_required
def listeM(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    
    if selected_category:
        menu = Menu.objects.filter(category__name=selected_category)
    else:
        menu = Menu.objects.all()

    return render(request, "api/spa/listeM.html", {'menu': menu, 'categories': categories})



@login_required
def add_or_update_ingredient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = int(request.POST.get('quantity', 0))  

        ingredient, created = Ingredient.objects.get_or_create(name=name)
        if created:
            messages.success(request, 'Ingredient added successfully.')
        else:
            messages.error(request, 'Ingredient already exists.')

        return HttpResponseRedirect(reverse('api:add_ingredient'))

    ingredients = Ingredient.objects.select_related('stock').all()
    return render(request, 'api/spa/add_ingredient.html', {'ingredients': ingredients})


@login_required
def delete_ingredient(request, ingredient_id):
    ingredient = Ingredient.objects.get(id=ingredient_id)
    ingredient.delete()
    return HttpResponseRedirect(reverse('api:add_ingredient'))



@login_required
def edit(request, id):
    menu_item = get_object_or_404(Menu, id=id)
    ingredients = Ingredient.objects.all()
    categories = Category.objects.all()
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            updated_menu_item = form.save()
            selected_ingredients = request.POST.getlist('ingredients')
            updated_menu_item.ingredients.clear()
            updated_menu_item.ingredients.add(*selected_ingredients)
            updated_menu_item.save()
            messages.success(request, "Menu item updated successfully.")
            return redirect("api:listeM")
    else:
        form = MenuForm(instance=menu_item)
    return render(request, 'api/spa/edit.html', {
        'menu': menu_item,
        'form': form,
        'ingredients': ingredients,
        'categories': categories,
    })



@login_required
def update(request, id):
    menu = Menu.objects.get(id=id)
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            form.save()
            return redirect("api:listeM")
    else:
        form = MenuForm(instance=menu)
    return render(request, 'api/spa/edit.html', {'menu': menu, 'form': form})


@login_required
def delete(request, id):
    menu = Menu.objects.get(id=id)
    menu.delete()
    return redirect("api:listeM")

def createOrder(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        menu = Menu.objects.filter(category__name=selected_category)
    else:
        menu = Menu.objects.all()
        categories = Category.objects.all()
    selected_category = request.GET.get('category')
    
    zero_stock_ingredients = Stock.objects.filter(quantity=0).values_list('ingredient', flat=True)
    
    if selected_category:
        menu = Menu.objects.filter(category__name=selected_category).exclude(ingredients__in=zero_stock_ingredients)
    else:
        menu = Menu.objects.exclude(ingredients__in=zero_stock_ingredients)
    return render(request, 'api/spa/order.html', {'menu': menu, 'categories': categories})

@login_required
def manage_stock(request):
    ingredients = Ingredient.objects.select_related('stock').all()
    return render(request, 'api/spa/manage_stock.html', {'ingredients': ingredients})

@login_required
def stock_detail(request, ingredient_id):
    try:
        stock = Stock.objects.get(ingredient__id=ingredient_id)
        return JsonResponse({'quantity': stock.quantity})
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)


@login_required
def stock_quantities(request):
    data = {stock.ingredient.id: stock.quantity for stock in Stock.objects.all()}
    return JsonResponse(data)

logger = logging.getLogger(__name__)


@login_required
@require_POST
@csrf_exempt
def set_stock(request, ingredient_id):
    try:
        data = json.loads(request.body)
        quantity = data.get('quantity')
        if quantity is None:
            raise ValueError("Quantity is required and must be an integer.")

        ingredient = Ingredient.objects.get(pk=ingredient_id)
        stock, created = Stock.objects.get_or_create(ingredient=ingredient)
        stock.quantity = quantity
        stock.save()
        return JsonResponse({'quantity': stock.quantity})
    except Ingredient.DoesNotExist:
        logger.error(f'Ingredient not found for ID {ingredient_id}')
        return JsonResponse({'error': 'Ingredient not found'}, status=404)
    except ValueError as ve:
        logger.error(f'Value error: {ve}')
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

@login_required
def add_stock(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
    stock, created = Stock.objects.get_or_create(ingredient=ingredient)
    if not created:
        stock.quantity += 1
    else:
        stock.quantity = 1  
    stock.save()
    return JsonResponse({'quantity': stock.quantity, 'ingredient_id': ingredient_id})

@login_required
def remove_stock(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
    stock = get_object_or_404(Stock, ingredient=ingredient)
    if stock.quantity > 0:
        stock.quantity -= 1
        stock.save()
        return JsonResponse({'quantity': stock.quantity, 'ingredient_id': ingredient_id})
    else:
        return JsonResponse({'quantity': stock.quantity, 'ingredient_id': ingredient_id, 'error': 'Stock is already empty'})


@login_required
def table_list(request):
    tables = DiningTable.objects.all()
    return render(request, 'api/spa/table_list.html', {'tables': tables})

@login_required
def table_detail(request, table_id):
    table = get_object_or_404(DiningTable, pk=table_id)
    orders = table.order_set.all()
    return render(request, 'api/spa/table_detail.html', {'table': table, 'orders': orders})

@require_POST
def update_table_status(request, table_id):
    table = get_object_or_404(DiningTable, pk=table_id)
    if table.status == 'available':
        table.status = 'occupied'
    else:
        table.status = 'available'
    table.save()
    return redirect('api:table_detail', table_id=table_id)


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    items_data = order.items 
    menus = Menu.objects.filter(id__in=items_data.keys()) 
    items = {menu: items_data.get(str(menu.id), 0) for menu in menus}

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if 'update_status' in request.POST:
            if form.is_valid():
                form.save()
                return redirect('api:table_detail', table_id=order.table.id)
        elif 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            if item_id in items_data:
                del items_data[item_id] 
                order.items = items_data 
                order.save()
                return redirect('api:update_order_status', order_id=order_id)
        elif 'delete_order' in request.POST:
            table_id = order.table.id
            order.delete()
            return redirect('api:table_detail', table_id=table_id)
    else:
        form = OrderForm(instance=order)

    return render(request, 'api/spa/update_order.html', {
        'form': form,
        'order': order,
        'items': items,
        'total_price': order.total_price,
        'note': order.note
    })


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'api/spa/add_category.html', {'categories': categories})


@login_required
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
          
            return redirect('api:add_category')  
    else:
        form = CategoryForm()
    
    categories = Category.objects.all()
    return render(request, 'api/spa/add_category.html', {'form': form, 'categories': categories})


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect(reverse('api:add_category'))
    else:
        form = CategoryForm(instance=category)
    return render(request, 'api/spa/edit_category.html', {'form': form, 'category': category})


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect(reverse('api:add_category'))


@login_required
def view_orders(request):
    date_query = request.GET.get('date')  
    if date_query:
        date = parse_date(date_query)  
        all_orders = Order.objects.filter(created_at__date=date).order_by('-created_at')
    else:
        all_orders = Order.objects.all().order_by('-created_at')

    total_profit = all_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'orders': all_orders,
        'total_profit': total_profit,
        'date_requested': date_query
    }
    
    return render(request, 'api/spa/sales_report.html', context)


