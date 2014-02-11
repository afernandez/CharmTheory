from django import template

register = template.Library()


@register.filter(name="modulo")
def modulo(value, divisor):
    return value % divisor

@register.filter(name="column")
def modulo_plus_one(value, divisor):
    return (value % divisor) + 1

@register.filter(name="int_div")
def int_div(value, divisor):
    return int(value / divisor)

@register.filter(name="int_div_plus_one")
def int_div_plus_one(value, divisor):
    return int(value / divisor) + 1