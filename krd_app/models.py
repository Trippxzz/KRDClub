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




###LOGISTICA
class Compra(models.Model):
    proveedor = models.CharField(max_length=25)
    fecha = models.DateField()
    folio = models.CharField(max_length=20)
    subtotalc = models.IntegerField()

class ProductoCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="productos_compra")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_compra = models.IntegerField()
    precio_und = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal_prod = models.DecimalField(max_digits=10,decimal_places=0, default=0)

    def save(self, *args, **kwargs):
        self.subtotal_prod = self.cantidad_compra * self.precio_und
        super().save(*args, **kwargs)

class vehiculo(models.Model):
    MARCAS = [
        ('Audi', 'Audi'),
        ('BMW', 'BMW'),
        ('Mercedes-Benz', 'Mercedes-Benz'),
        ('Porsche', 'Porsche'),
        ('Volkswagen', 'Volkswagen')
    ]
    marca = models.CharField(max_length=50, choices=MARCAS)
    modelo = models.CharField(max_length=100)
    cilindrada = models.DecimalField(max_digits=4, decimal_places=1, help_text="Ejemplo: 2.0")
    anio = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.marca} {self.modelo} {self.cilindrada}L ({self.anio})"