"""
URL configuration for krdweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from krd_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("catalogo/", views.getCatalogo, name="listar_productos"),
    path("catalogo/crearprod/", views.addProducto, name="crear_producto"),
    path("catalogo/<uuid:id>", views.getProducto, name="detproducto"),
    path("crearcompra/", views.addCompra, name="crear_compra"),
    path('vehiculos/agregar/', views.agregar_vehiculos, name='agregar_vehiculos'),
    path('vehiculos/lista/', views.lista_vehiculo, name='lista_vehiculo'),
    path('vehiculos/eliminar/<int:pk>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    path('catalogo/<uuid:id>/editar/', views.editProducto, name='editar_producto'),
    path('imagen/eliminar/<int:imagen_id>/', views.eliminar_imagen, name='eliminar_imagen'),
    path('imagen/principal/<int:imagen_id>/', views.cambiar_principal, name='cambiar_principal'),
    path('catalogo/<uuid:id>/eliminar/', views.eliminarProducto, name='eliminar_producto'),
    path('compras/crear/', views.addCompra, name='crear_compra'),
    path('compras/', views.listar_compras, name='listar_compras'),
    path('carrito/', views.getCarrito, name='ver_carrito'),
    path('agregar/<uuid:producto_id>/', views.addCarrito, name='agregar_al_carrito'),
    path('quitar/<uuid:producto_id>/', views.eliminardelCarrito, name='remover_del_carrito'),
    path('procesarCompra', views.procesarCompra, name='procesar_compra'),
    path('contador_carrito/', views.contador_carrito, name='contador_carrito'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)