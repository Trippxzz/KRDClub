import uuid
from django.db import models
from django.utils import timezone
# Create your models here.


class Producto(models.Model):
    id_producto = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    n_producto=models.CharField(max_length=60)
    desc_producto=models.CharField(max_length=200)
    stock = models.IntegerField(default=0)
    precio=models.IntegerField()
    # imagen=models.ImageField(upload_to="prodimagen") ##Se guardara de forma local hasta cambiar modo de almacenamiento en hosting
    aro = models.IntegerField()
    apernadura=models.CharField(max_length=7)
    ancho=models.CharField(max_length=5)
    offset=models.IntegerField()
    centro_llanta=models.CharField(max_length=5)

    def __str__(self):
        return self.n_producto
    

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="prodimagen")

    def __str__(self):
        return f"Imagen de {self.producto.n_producto}"

