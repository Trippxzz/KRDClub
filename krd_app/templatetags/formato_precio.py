from django import template
import locale

register = template.Library()

@register.filter(name='formato_miles')
def formato_miles(value):
    """
    Formatea un número con separadores de miles usando puntos.
    Ejemplo: 1500000 -> 1.500.000
    """
    try:
        # Convertir a entero para quitar decimales
        numero = int(float(value))
        # Formatear con separadores de miles (puntos)
        return '{:,.0f}'.format(numero).replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter(name='precio_clp')
def precio_clp(value):
    """
    Formatea un precio en formato CLP con símbolo $ y separadores de miles.
    Ejemplo: 1500000 -> $1.500.000
    """
    try:
        numero = int(float(value))
        return '${:,.0f}'.format(numero).replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Obtiene un item de un diccionario por clave.
    Útil para acceder a diccionarios en templates.
    Uso: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return 0
    try:
        return dictionary.get(key, 0)
    except (AttributeError, TypeError):
        return 0
