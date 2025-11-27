from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Compra, ProductoCompra, vehiculo, Usuario, ProductoImagen, Venta
from datetime import date
from django.contrib.auth.forms import UserCreationForm ##Para la creacion de usuarios, se usará para completar datos al momento de comprar


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ("id_producto", "stock", "sprite_360", "sprite_cols", "sprite_rows", "sprite_total")
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

class MultipleFileInput(forms.ClearableFileInput):
    """Widget personalizado para múltiples archivos"""
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    """Campo personalizado para múltiples archivos"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ProductoImagenForm(forms.Form):
    """Form para subir imágenes del producto"""
    imagenes = MultipleFileField(
        required=False,
        label='Seleccionar imágenes',
        help_text='Puedes seleccionar múltiples imágenes'
    )
    es_360 = forms.BooleanField(
        required=False,
        label='¿Son imágenes 360°?',
        help_text='Marca esta casilla si vas a subir múltiples imágenes para vista 360°'
    )

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        exclude = ("subtotalc",)
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'text',
                'class': 'fecha-picker',
                'placeholder': 'Seleccionar fecha',
                'autocomplete': 'off'
            }),
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


