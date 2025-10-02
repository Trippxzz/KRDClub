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
    aro = models.IntegerField()
    apernadura=models.CharField(max_length=7)
    ancho=models.CharField(max_length=5)
    offset=models.IntegerField()
    centro_llanta=models.CharField(max_length=5)

    def __str__(self):
        return self.n_producto
    def imagen_principal(self):
        return self.imagenes.filter(es_principal=True).first()
    

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="prodimagen")
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"Imagen de {self.producto.n_producto}"

    def save(self, *args, **kwargs):
        if self.es_principal:
            ProductoImagen.objects.filter(producto=self.producto, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)