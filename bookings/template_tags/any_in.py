from django import template

register = template.Library()


@register.filter
def any_in(list, string):
    return any(string in s for s in list)
