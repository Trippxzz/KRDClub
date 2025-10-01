from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Producto, ProductoImagen
from .forms import ProductoForm, ProductoImagenForm
from django.http import HttpResponse

### SECCION POST (FORMS)
def addProducto(request):
    if request.method == "POST":
        form_producto = ProductoForm(request.POST)
        form_imagenes = ProductoImagenForm(request.POST, request.FILES or None)

        if form_producto.is_valid():
            producto = form_producto.save()
            messages.success(request, "Producto creado con éxito")
            #PARA GUARDAR VARIAS IMAGENES
            for img in request.FILES.getlist('imagenes'):
                ProductoImagen.objects.create(producto=producto, imagen = img)

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
        

### SECCION GET (MODELS)
def getProducto(request):
    if request.method=="GET":
        prods=Producto.objects.all()
        return render(request, "catalogo.html", {"prods":prods})