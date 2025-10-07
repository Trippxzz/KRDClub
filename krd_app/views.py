from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Producto, ProductoImagen, Compra, ProductoCompra
from .forms import ProductoForm, ProductoImagenForm, CompraForm, ProductoCompraForm
from django.http import HttpResponse
from decimal import Decimal
import json
### SECCION POST (FORMS)
def addProducto(request):
    if request.method == "POST":
        form_producto = ProductoForm(request.POST)
        form_imagenes = ProductoImagenForm(request.POST, request.FILES or None)

        if form_producto.is_valid():
            producto = form_producto.save()
            messages.success(request, "Producto creado con éxito")
            #PARA GUARDAR VARIAS IMAGENES
            for i, img in enumerate(request.FILES.getlist('imagenes')):
                ProductoImagen.objects.create(
                    producto=producto,
                    imagen=img,
                    es_principal=True if i == 0 else False  # para asignar la primera imagen que se selecciona como principal
                )


            messages.success(request, "Producto creado con éxito")
            return redirect("/catalogo/")
        else:
            print("error prod:",form_producto.errors)
            print("error img:",form_imagenes.errors)
            return render(request,"catalogo.html")
            # messages.error(request,"Error, probablemente usaste un formato no soportado")
            # 
    else:
        form_producto = ProductoForm()
        form_imagenes = ProductoImagenForm()
        return render(request,"crear/crearprods.html",{"form_producto":form_producto, "form_imagenes":form_imagenes})
        
def addCompra(request):
    if request.method == "POST":
        form = CompraForm(request.POST)
        productos_data = json.loads(request.POST.get("productos_data", "[]"))

        if form.is_valid():
            compra = form.save(commit=False)
            compra.subtotalc = 0
            compra.save()

            subtotal_total = 0
            for p in productos_data:
                # Aquí sí buscamos el Producto, no ProductoCompra
                prod = Producto.objects.get(id_producto=p["producto"])
                cantidad = int(p["cantidad"])
                precio = Decimal(p["precio"])
                
                # Creamos el ProductoCompra directamente
                pc = ProductoCompra.objects.create(
                    compra=compra,
                    producto=prod,
                    cantidad_compra=cantidad,
                    precio_und=precio
                )

                # Actualizamos stock del producto
                prod.stock += cantidad
                prod.save()

                subtotal_total += pc.subtotal_prod

            compra.subtotalc = subtotal_total
            compra.save()

            return redirect("/catalogo/")

    else:
        form = CompraForm()

    return render(request, "compras/crearcompra.html", {
        "form": form,
        "productos": Producto.objects.all()
    })



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