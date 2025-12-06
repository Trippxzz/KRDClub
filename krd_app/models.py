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


### Seccion Valoraciones / Reseñas

class Valoracion(models.Model):
    """
    Sistema simple de valoración de ventas por parte de los clientes.
    """
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='valoracion')
    rut_usuario = models.CharField(max_length=12)
    
    # Valoración en estrellas (1-5)
    estrellas = models.PositiveIntegerField(default=5)
    
    # Comentario opcional
    comentario = models.TextField(max_length=500, blank=True, null=True)
    
    # Metadatos
    fecha_valoracion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        ordering = ['-fecha_valoracion']
    
    def __str__(self):
        return f"Valoración Venta #{self.venta.id} - {self.estrellas}⭐"
    
    @property
    def nombre_usuario(self):
        """Obtiene el nombre del usuario que valoró"""
        try:
            usuario = Usuario.objects.get(rut=self.rut_usuario)
            return f"{usuario.nombre} {usuario.apellido[0]}."
        except Usuario.DoesNotExist:
            return "Cliente"


### Seccion Configuración del Sistema

class Configuracion(models.Model):
    """
    Tabla de configuraciones del sistema.
    Almacena ajustes configurables por el admin como:
    - umbral_bajo_stock: cantidad para considerar bajo stock
    - anuncio_activo: si mostrar anuncio o no
    - anuncio_texto: texto del anuncio
    - anuncio_color: color de fondo del anuncio
    """
    clave = models.CharField(max_length=50, unique=True, primary_key=True)
    valor = models.TextField()
    descripcion = models.CharField(max_length=200, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"
    
    def __str__(self):
        return f"{self.clave}: {self.valor[:50]}"
    
    @classmethod
    def get_valor(cls, clave, default=None):
        """Obtiene el valor de una configuración por su clave"""
        try:
            return cls.objects.get(clave=clave).valor
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_valor(cls, clave, valor, descripcion=''):
        """Crea o actualiza una configuración"""
        obj, created = cls.objects.update_or_create(
            clave=clave,
            defaults={'valor': valor, 'descripcion': descripcion}
        )
        return obj


### Sección Cupones de Descuento

class Cupon(models.Model):
    """
    Sistema de cupones de descuento para aplicar en el checkout.
    """
    TIPO_CHOICES = [
        ('porcentaje', 'Porcentaje'),
        ('monto', 'Monto Fijo'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    descripcion = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='porcentaje')
    valor = models.IntegerField(help_text="Porcentaje (ej: 10) o monto fijo (ej: 5000)")
    
    # Restricciones
    monto_minimo = models.IntegerField(default=0, help_text="Monto mínimo de compra para aplicar")
    uso_maximo = models.IntegerField(default=0, help_text="0 = ilimitado")
    usos_actuales = models.IntegerField(default=0)
    
    # Vigencia
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cupón"
        verbose_name_plural = "Cupones"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        if self.tipo == 'porcentaje':
            return f"{self.codigo} - {self.valor}% OFF"
        return f"{self.codigo} - ${self.valor} OFF"
    
    def es_valido(self, monto_carrito=0):
        """Verifica si el cupón es válido para usar"""
        from django.utils import timezone
        hoy = timezone.now().date()
        
        if not self.activo:
            return False, "Cupón inactivo"
        
        if self.fecha_inicio and hoy < self.fecha_inicio:
            return False, "Cupón aún no vigente"
        
        if self.fecha_fin and hoy > self.fecha_fin:
            return False, "Cupón expirado"
        
        if self.uso_maximo > 0 and self.usos_actuales >= self.uso_maximo:
            return False, "Cupón agotado"
        
        if monto_carrito < self.monto_minimo:
            return False, f"Monto mínimo: ${self.monto_minimo:,}".replace(',', '.')
        
        return True, "Válido"
    
    def calcular_descuento(self, monto):
        """Calcula el descuento a aplicar"""
        if self.tipo == 'porcentaje':
            return int(monto * self.valor / 100)
        return min(self.valor, monto)  # El descuento no puede ser mayor al monto
    
    def usar(self):
        """Incrementa el contador de usos"""
        self.usos_actuales += 1
        self.save()

