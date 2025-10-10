from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, ProductoImagen, Compra, ProductoCompra, vehiculo
from .forms import ProductoForm, ProductoImagenForm, CompraForm, ProductoCompraForm, VehiculoForm
from django.http import HttpResponse
from decimal import Decimal
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
    



###SECCION DE EDITS

def editProducto(request, id):
    prod = get_object_or_404(Producto, id_producto=id)
    imgs = prod.imagenes.all()
    vehiculos = vehiculo.objects.all()
    if request.method == "POST":
        print("POST recibido en editProducto")
        print("POST data:", request.POST)
        print("FILES:", request.FILES)
        form_producto = ProductoForm(request.POST, instance=prod)
        print("form_producto.is_valid():", form_producto.is_valid())
        print("form errors:", form_producto.errors)
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