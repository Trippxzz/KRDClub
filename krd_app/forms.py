from django import forms
from .models import Producto
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