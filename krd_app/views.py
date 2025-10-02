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