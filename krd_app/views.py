from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Producto
from .forms import ProductoForm
from django.http import HttpResponse

### SECCION POST (FORMS)
def addProducto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado con éxito")
            return redirect("/catalogo/")
        else:
            messages.error(request,"Error, probablemente usaste un formato no soportado")
            return render(request,"catalogo.html")
    else:
        form = ProductoForm()
        return render(request,"crear/crearprods.html",{"formulario":form})
        

### SECCION GET (MODELS)
def getProducto(request):
    if request.method=="GET":
        print("2")
        prods=Producto.objects.all()
        return render(request, "catalogo.html", {"prods":prods})