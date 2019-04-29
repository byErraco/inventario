from django import template

register = template.Library()

@register.filter(name='dict_key')
def dict_key(d, k):
    return d.get(k)