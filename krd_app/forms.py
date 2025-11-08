from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Compra, ProductoCompra, vehiculo, Usuario
from datetime import date
from django.contrib.auth.forms import UserCreationForm ##Para la creacion de usuarios, se usará para completar datos al momento de comprar


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ("id_producto", "stock")
        labels = {
            'n_producto': 'Nombre del producto',
            'desc_producto': 'Descripción del producto',
            'precio': 'Precio',
            'aro': 'Aro',
            'apernadura': 'Apernadura',
            'ancho': 'Ancho',
            'offset': 'Offset',
            'centro_llanta': 'Centro de llanta',
        }
        widgets = {
            'desc_producto': forms.Textarea(),
        }

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ProductoImagenForm(forms.Form):
    imagenes = forms.ImageField(widget=MultiFileInput(attrs={'multiple': True}), required=False)

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        exclude = ("subtotalc",)
        widgets = {
            'pdf': forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
        }

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Solo se permiten archivos PDF.")
            if pdf.content_type != 'application/pdf':
                raise forms.ValidationError("El archivo debe ser un PDF.")
        return pdf

class ProductoCompraForm(forms.ModelForm):
    class Meta:
        model = ProductoCompra
        exclude=("compra", "subtotal_prod")

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = vehiculo
        fields = ['marca', 'modelo', 'cilindrada', 'anio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        self.fields['anio'].widget = forms.Select(
            choices=[(y, y) for y in range(2000, current_year + 1)]
        )

class UsuarioForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ['rut', 'nombre', 'apellido', 'email']
    rut=forms.CharField(label="Rut")
    nombre=forms.CharField(label="Nombre")
    apellido=forms.CharField(label="Apellido")
    email=forms.CharField(label="Correo electronico")
    telefono=forms.CharField(label="Telefono")
    direccion=forms.CharField(label="Direccion")
