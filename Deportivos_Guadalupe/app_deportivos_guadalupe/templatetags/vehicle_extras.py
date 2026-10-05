from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def thousands_dot(value):
    try:
        return f'{Decimal(str(value)):,.0f}'.replace(',', '.')
    except (InvalidOperation, TypeError, ValueError):
        return value
