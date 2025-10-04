from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Compra, ProductoCompra
from django.contrib.auth.forms import UserCreationForm ##Para la creacion de usuarios, se usará para completar datos al momento de comprar


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ("id_producto", "stock")
    n_producto=forms.CharField(label="Nombre del producto")
    desc_producto=forms.CharField(widget=forms.widgets.Textarea, label="Descripción del producto")
    precio=forms.IntegerField(label="Precio")
    # imagen=forms.ImageField(label="Imagen")
    aro=forms.IntegerField()
    apernadura=forms.CharField()
    ancho=forms.CharField()
    offset=forms.IntegerField()
    centro_llanta=forms.CharField()

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ProductoImagenForm(forms.Form):
    imagenes = forms.ImageField(widget=MultiFileInput(attrs={'multiple': True}), required=False)

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        exclude = ("subtotalc",)
    proveedor = forms.CharField()
    fecha = forms.DateField()
    folio = forms.CharField()

class ProductoCompraForm(forms.ModelForm):
    class Meta:
        model = ProductoCompra
        exclude=("compra", "subtotal_prod")

ProductoCompraFormSet = inlineformset_factory(
    Compra, ProductoCompra, form=ProductoCompraForm, extra = 1, can_delete = True) ##Ese extra hará que siempre haya una linea mas para insertar un producto
