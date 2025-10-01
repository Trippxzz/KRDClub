from django.contrib import admin
from .models import Producto, ProductoImagen
# Register your models here.

class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [ProductoImagenInline]

admin.site.register(ProductoImagen)
