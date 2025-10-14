from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, ProductoImagen, Compra, ProductoCompra, vehiculo, Producto_Vehiculo, Venta, Producto_Venta
from .forms import ProductoForm, ProductoImagenForm, CompraForm, ProductoCompraForm, VehiculoForm
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.db import transaction
from django.urls import reverse
import json
### SECCION POST (FORMS)
def addProducto(request):
    if request.method == "POST":
        form_producto = ProductoForm(request.POST)
        form_imagenes = ProductoImagenForm(request.POST, request.FILES or None)

        if form_producto.is_valid():
            producto = form_producto.save()
            # Tomar todas las imágenes subidas
            imagenes = request.FILES.getlist('imagenes')
            # Tomar el índice de la imagen marcada como principal desde el formulario (input hidden)
            principal_idx = int(request.POST.get('principal_idx', 0))
            # Recorrer las imágenes y marcar la principal según el índice seleccionado
            for i, img in enumerate(imagenes):
                ProductoImagen.objects.create(
                    producto=producto,
                    imagen=img,
                    es_principal=True if i == principal_idx else False  # Solo la seleccionada queda como principal
                )

            messages.success(request, "Producto creado con éxito")
            return redirect("/catalogo/")
        else:
            print("error prod:",form_producto.errors)
            print("error img:",form_imagenes.errors)
            return render(request,"catalogo.html")
    else:
        form_producto = ProductoForm()
        form_imagenes = ProductoImagenForm()
        return render(request,"crear/crearprods.html",{"form_producto":form_producto, "form_imagenes":form_imagenes})
    
def addCompra(request):
    if request.method == "POST":
        form = CompraForm(request.POST, request.FILES)
        productos_data = json.loads(request.POST.get("productos_data", "[]"))

        if form.is_valid():
            compra = form.save(commit=False)
            compra.subtotalc = 0
            compra.save()

            subtotal_total = 0
            for p in productos_data:
                prod = Producto.objects.get(id_producto=p["producto"])
                cantidad = int(p["cantidad"])
                precio = Decimal(p["precio"])
                pc = ProductoCompra.objects.create(
                    compra=compra,
                    producto=prod,
                    cantidad_compra=cantidad,
                    precio_und=precio
                )
                prod.stock += cantidad
                prod.save()
                subtotal_total += pc.subtotal_prod

            compra.subtotalc = subtotal_total
            compra.save()

            return redirect("listar_compras")
    else:
        form = CompraForm()

    return render(request, "compras/crearcompra.html", {
        "form": form,
        "productos": Producto.objects.all()
    })

def listar_compras(request):
    compras = Compra.objects.all()
    return render(request, "compras/listarcompras.html", {"compras": compras})

def agregar_vehiculos(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vehiculo')
    else:
        form = VehiculoForm()
    return render(request, 'agregar_vehiculos.html', {'form': form})

def lista_vehiculo(request):
    vehiculos = vehiculo.objects.all()
    return render(request, 'lista_vehiculo.html', {'vehiculos': vehiculos})

def eliminar_vehiculo(request, pk):
    veh = get_object_or_404(vehiculo, pk=pk)
    if request.method == "POST":
        veh.delete()
        return redirect('lista_vehiculo')
    return render(request, 'krd/confirmar_eliminacion.html', {'vehiculo': veh})

def addCarrito(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    carrito = request.session.get('carrito', {})
    cantidad = 1
    try:
        cantidad = int(request.GET.get('cantidad', '1'))
        if cantidad < 1:
            cantidad = 1
    except Exception:
        cantidad = 1

    id_str = str(producto_id)
    if id_str in carrito:
        carrito[id_str]['cantidad'] += cantidad
        carrito[id_str]['subtotal'] = carrito[id_str]['cantidad'] * carrito[id_str]['precio']
    else:
        carrito[id_str] = {
            'nombre': producto.n_producto,
            'precio': producto.precio,
            'cantidad': cantidad,
            'subtotal': producto.precio * cantidad
        }
    request.session['carrito'] = carrito
    request.session.modified = True
    # Redirigir de vuelta a la página del producto con mensaje de éxito
    return redirect(f"/catalogo/{producto_id}?mensaje=ok")


### SECCION GET (MODELS)
def getCatalogo(request):
    if request.method=="GET":
        prods=Producto.objects.all()
        return render(request, "catalogo.html", {"prods":prods})
    

def getProducto(request, id):
    if request.method == "GET":
        prod = Producto.objects.get(id_producto=id)
        imgprod = prod.imagenes.all()
        return render(request, "producto.html", {"prod":prod, "imgs":imgprod})
    

def getCarrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['subtotal'] for item in carrito.values())
    return render(request, 'carrito.html', {'carrito': carrito, 'total': total})

###SECCION DE EDITS

def editProducto(request, id):
    prod = get_object_or_404(Producto, id_producto=id)
    imgs = prod.imagenes.all()
    vehiculos = vehiculo.objects.all()
    # Obtener vehículos asociados para inicializar el JS
    vehiculos_asociados_qs = Producto_Vehiculo.objects.filter(producto=prod).select_related('vehiculo')
    vehiculos_asociados = [
        {
            'id': str(vv.vehiculo.id),
            'text': f"{vv.vehiculo.marca}, {vv.vehiculo.modelo}, {vv.vehiculo.cilindrada}, {vv.vehiculo.anio}"
        }
        for vv in vehiculos_asociados_qs
    ]
    if request.method == "POST":
        form_producto = ProductoForm(request.POST, instance=prod)
        if form_producto.is_valid():
            producto = form_producto.save()
            # Guardar nuevas imágenes si se subieron
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                ProductoImagen.objects.create(
                    producto=producto,
                    imagen=img,
                    es_principal=False
                )
            # Guardar aplicaciones del producto (vehículos asociados)
            vehiculos_ids = request.POST.get('vehiculos_ids', '')
            # Eliminar relaciones previas
            Producto_Vehiculo.objects.filter(producto=producto).delete()
            # Crear nuevas relaciones
            if vehiculos_ids:
                for v_id in vehiculos_ids.split(','):
                    if v_id:
                        Producto_Vehiculo.objects.create(producto=producto, vehiculo_id=v_id)
            messages.success(request, "Producto editado con éxito")
            return redirect("/catalogo/")
        else:
            from django.contrib import messages as dj_messages
            return render(request, "editar/editarprod.html", {
                "form_producto": form_producto,
                "form_imagenes": ProductoImagenForm(),
                "prod": prod,
                "imgs": imgs,
                "vehiculos": vehiculos,
                "vehiculos_asociados": vehiculos_asociados,
                "messages": dj_messages.get_messages(request)
            })
    else:
        form_producto = ProductoForm(instance=prod)
        from django.contrib import messages as dj_messages
        return render(request, "editar/editarprod.html", {
            "form_producto": form_producto,
            "form_imagenes": ProductoImagenForm(),
            "prod": prod,
            "imgs": imgs,
            "vehiculos": vehiculos,
            "vehiculos_asociados": vehiculos_asociados,
            "messages": dj_messages.get_messages(request)
        })

def cambiar_principal(request, imagen_id):
    imagen = get_object_or_404(ProductoImagen, id=imagen_id)
    producto = imagen.producto
    if request.method == "POST":
        # Desmarcar todas las imágenes como principal
        ProductoImagen.objects.filter(producto=producto).update(es_principal=False)
        # Marcar la seleccionada como principal
        imagen.es_principal = True
        imagen.save()
        messages.success(request, "Imagen principal actualizada.")
        return redirect(reverse('editar_producto', args=[producto.id_producto]))
    return HttpResponse("Método no permitido", status=405)
def eliminar_imagen(request, imagen_id):
    imagen = get_object_or_404(ProductoImagen, id=imagen_id)
    producto_id = imagen.producto.id_producto
    if request.method == "POST":
        imagen.delete()
        messages.success(request, "Imagen eliminada correctamente.")
        return redirect(reverse('editar_producto', args=[producto_id]))
    return HttpResponse("Método no permitido", status=405)


##Seccion Eliminar

def eliminarProducto(request, id):
    prod = get_object_or_404(Producto, id_producto=id)
    if request.method == "POST":
        prod.delete()
        messages.success(request, "Producto eliminado con éxito")
        return redirect("/catalogo/")
    
def eliminardelCarrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    id_str = str(producto_id)
    if id_str in carrito:
        del carrito[id_str]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, "Producto eliminado del carrito.")
    return redirect('/catalogo/')


### SECCION CONTROL DE STOCK Y SEGURIDAD
@transaction.atomic
def procesarCompra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect("ver_carrito")

    try:
        with transaction.atomic():
            total = sum(item["subtotal"] for item in carrito.values())
            cantidad_total = sum(item["cantidad"] for item in carrito.values())

            venta = Venta.objects.create(
                cantidad=cantidad_total,
                precio_venta=total,
            )

            for id_producto, item in carrito.items():
                producto = Producto.objects.select_for_update().get(id_producto=id_producto)

                if producto.stock < item["cantidad"]:
                    raise ValueError(f"No hay suficiente stock para {producto.n_producto}")

                producto.stock -= item["cantidad"]
                producto.save()

                Producto_Venta.objects.create(
                    id_venta=venta,
                    id_producto=producto,
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"]
                )

            # Vaciar carrito
            request.session["carrito"] = {}
            request.session.modified = True
            messages.success(request, "Compra realizada con éxito 🎉")

    except ValueError as e:
        messages.error(request, str(e))
        return redirect("ver_carrito")

    return redirect("/catalogo/")

### Contador carrito
def contador_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return JsonResponse({"total_items": total_items})