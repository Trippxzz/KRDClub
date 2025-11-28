import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager 
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
    # Sprite 360 - Una sola imagen que contiene todas las vistas
    sprite_360 = models.ImageField(upload_to="sprites/", null=True, blank=True)
    sprite_cols = models.IntegerField(default=6)  # Columnas en el sprite
    sprite_rows = models.IntegerField(default=6)  # Filas en el sprite
    sprite_total = models.IntegerField(default=36)  # Total de frames

    def __str__(self):
        return self.n_producto
    def imagen_principal(self):
        return self.imagenes.filter(es_principal=True).first()
    

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="prodimagen")
    es_principal = models.BooleanField(default=False)
    es_360 = models.BooleanField(default=False) 
    orden = models.IntegerField(default=0)  # Para ordenar las imágenes 360
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
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)

class ProductoCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="productos_compra")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_compra = models.IntegerField()
    precio_und = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal_prod = models.DecimalField(max_digits=10,decimal_places=0, default=0)

    def save(self, *args, **kwargs):
        self.subtotal_prod = self.cantidad_compra * self.precio_und
        super().save(*args, **kwargs)


### Seccion de vehiculos/aplicaciones

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
    

class Producto_Vehiculo(models.Model): ##PARA CREARLE APLICACIONES A LOS PRODUCTOS
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(vehiculo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto.n_producto} compatible con {self.vehiculo}"


### Seccion de ventas

class Venta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de procesamiento'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # id_venta eliminado: se usará el id autoincremental por defecto
    id_usuario = models.CharField(max_length=50, null=True, blank=True)  # si no hay login
    # cantidad = models.IntegerField(default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=0)
    fecha_venta = models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return f"Venta {self.id} - {self.fecha_venta.date()} - {self.get_estado_display()}"


class Producto_Venta(models.Model):
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="productos_venta")
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_producto.n_producto} x{self.cantidad}"


### Seccion Logistica (Envíos)

class Logistica(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Envío'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]
    
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='logistica')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    empresa_envio = models.CharField(max_length=50, null=True, blank=True)
    n_seguimiento = models.CharField(max_length=50, null=True, blank=True)
    fecha_envio = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Logística Venta #{self.venta.id} - {self.get_estado_display()}"

    class Meta:
        verbose_name = "Logística"
        verbose_name_plural = "Logísticas"


### Seccion Usuario

class Usuario(AbstractBaseUser):
    rut = models.CharField(primary_key=True, max_length=12, unique=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    telefono = models.IntegerField()
    direccion = models.CharField(max_length=100)
    admin=models.BooleanField(default=False)

    USERNAME_FIELD="rut"

    REQUIRED_FIELDS=["nombre","apellido", "email", "telefono", "direccion"]
    def __str__(self):
        return f"{self.nombre}.{self.apellido}"
    def has_perm(self,perm,obj = None):
        return True
    def has_module_perms (self,app_label):
        return True
    @property
    def is_staff(self):
        return self.admin