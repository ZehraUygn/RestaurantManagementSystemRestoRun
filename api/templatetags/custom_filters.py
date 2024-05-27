from django import template

register = template.Library()

@register.filter
def get_attr(value, arg):
    return value.get(arg, 0) 

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)