"api/forms.py"
from django.forms import ModelForm, Textarea
from django import forms
from api.models import Menu,Ingredient, DiningTable, Order, Category, SurveyQuestion, SurveyResponse



class SignupForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'autocomplete': 'email'})
    )
    password = forms.CharField(
        label='Password',
        max_length=100,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    password = forms.CharField(
        label='Password',
        max_length=100,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class SurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = ['question_text', 'active']

class SurveyResponseForm(ModelForm):
    class Meta:
        model = SurveyResponse
        fields = ['rating', 'comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 5})
        }

class IngredientForm(forms.Form):
    name = forms.CharField(max_length=100, help_text='Enter the name of the ingredient')
    quantity = forms.IntegerField(min_value=0, help_text='Enter the stock quantity for the ingredient')
    
class MenuForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False),
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False)
    
    class Meta:
        model = Menu
        fields = ['name', 'image', 'price', 'ingredients','category']  

    def save(self, commit=True):
        menu = super().save(commit=False)
        if commit:
            menu.save()
            self.save_m2m()
        return menu


class CustomTableForm(forms.ModelForm):
    class Meta:
        model = DiningTable
        fields = ['table_number']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'note']  

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget = forms.Select(choices=Order.STATUS_CHOICES)
