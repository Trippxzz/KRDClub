import uuid
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Producto
from django.shortcuts import get_object_or_404

CARRO_CACHE_PREFIX = 'carro_'

def _carro_cache_key(carro_id):
    return f"{CARRO_CACHE_PREFIX}{carro_id}"

def generar_carro_id():
    return uuid.uuid4().hex

def get_carro_id_from_request(request):
    return request.COOKIES.get('carro_uuid')

def get_or_create_carro(request, response=None):
    carro_id = get_carro_id_from_request(request)
    if not carro_id:
        carro_id = generar_carro_id()
        set_cookie = True
    
    key = _carro_cache_key(carro_id)
    carro = cache.get(key)
    if carro is None:
        carro = {"items":{}, "meta":{"creado": timezone.now().isoformat()}}
        cache.set(key, carro, getattr(settings, 'CARRO_CACHE_TIMEOUT', 60 * 60 * 24 * 7)) ## Formato para 1 semana

    if set_cookie and response is not None:
        max_age = getattr(settings, 'CARRO_COOKIE_AGE', 60 * 60 * 24 * 7)  # 1 semana
        response.set_cookie('carro_uuid', carro_id, max_age=max_age, httponly=True, samesite="Lax")
    return carro, carro_id, set_cookie

def save_carro(carro_id, carro):
    key = _carro_cache_key(carro_id)
    cache.set(key, carro, getattr(settings, 'CARRO_CACHE_TIMEOUT', 60 * 60 * 24 * 7))

def add_producto_to_carro(carro_id, producto_id, cantidad=1):
    key = _carro_cache_key(carro_id)
    carro = cache.get(key) or {"items": {}, "meta": {"creado": timezone.now().isoformat()}}
    producto = get_object_or_404(Producto, id_producto=producto_id)
    pid = str(producto.producto_id)
    item= carro["items"].get(pid)
    if item:
        item['cantidad'] = int(item['cantidad']) + int(cantidad)
    else:
        item = {
            "cantidad": int(cantidad),
            "precio": int(producto.precio),
            "nombre": producto.n_producto,
            "aro": producto.aro,
        }
    carro["items"][pid] = item
    carro["meta"]["actualizado"] = timezone.now().isoformat()
    cache.set(key, carro, getattr(settings, 'CARRO_CACHE_TIMEOUT', 60 * 60 * 24 * 7))
    return carro

def update_prod_cant(carro_id, producto_uuid, cantidad):
    key = _carro_cache_key(carro_id)
    carro = cache.get(key)
    if not carro:
        raise ValueError("Carrito no encontrado")
    pid = str(producto_uuid)
    if pid not in carro["items"]:
        raise ValueError("Producto no en el carrito")
    if int(cantidad) <= 0:
        carro["items"].pop(pid, None)
    else:
        carro["items"][pid]["cantidad"] = int(cantidad)
    carro["meta"]["actualizado"] = timezone.now().isoformat()
    cache.set(key, carro, getattr(settings, 'CARRO_CACHE_TIMEOUT', 60 * 60 * 24 * 7))
    return carro

def remove_producto_from_carro(carro_id, producto_uuid):
    key = _carro_cache_key(carro_id)
    carro = cache.get(key)
    if not carro:
        return
    carro["items"].pop(str(producto_uuid), None)
    carro["meta"]["actualizado"] = timezone.now().isoformat()
    cache.set(key, carro, getattr(settings, 'CARRO_CACHE_TIMEOUT', 60 * 60 * 24 * 7))
    return carro

def clear_carro(carro_id):
    key = _carro_cache_key(carro_id)
    cache.delete(key)

def calcular_total(carro):
    total = Decimal(0)
    items = []
    for pid, item in carro.get("items", {}).items():
        subtotal = Decimal(item["precio"])
        cant = int(item["cantidad"])
        sub = subtotal * cant
        total += sub
        items.append({
            "id": pid,
            "nombre": item["nombre"],
            "aro": item["aro"],
            "cantidad": cant,
            "precio": subtotal,
            "subtotal": sub,
        })
    return {"total": total, "items": items}
