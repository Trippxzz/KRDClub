from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Producto, ProductoImagen, Compra
from .forms import ProductoForm, ProductoImagenForm, CompraForm, ProductoCompraFormSet
from django.http import HttpResponse
from decimal import Decimal

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
        formset = ProductoCompraFormSet(request.POST)

        if form.is_valid():
            compra = form.save(commit=False)
            compra.subtotalc = Decimal('0.00')
            compra.save()
            formset = ProductoCompraFormSet(request.POST, instance=compra)
            if formset.is_valid():
                subtotal_total = Decimal('0.00')
                productos = formset.save(commit=False)
                for prod in productos:
                    prod.compra = compra
                    prod.save()
                    prod.producto.stock += prod.cantidad_compra
                    prod.producto.save()
                    subtotal_total +=prod.subtotal_prod
                formset.save_m2m()
                compra.subtotalc = subtotal_total
                compra.save(update_fields=['subtotalc'])
                return redirect("/catalogo/")
            else:
                compra.delete()
    else:
        form = CompraForm()
        formset = ProductoCompraFormSet()

    return render(request, "compras/crearcompra.html", {"form": form, "formset":formset}) 

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