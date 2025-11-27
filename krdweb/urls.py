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
    path('', views.home, name='home'),
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
    path('checkout/', views.procesarCompra, name='procesar_compra'),
    path('buscar-usuario/', views.buscar_usuario_rut, name='buscar_usuario_rut'),
    path('webpay/', views.webpay_iniciar, name='webpay_iniciar'),
    path('webpay/retorno/', views.webpay_retorno, name='webpay_retorno'),
    path('contador_carrito/', views.contador_carrito, name='contador_carrito'),
    
    # API Filtro de Vehículos
    path('api/modelos/', views.get_modelos_por_marca, name='get_modelos'),
    path('api/cilindradas/', views.get_cilindradas_por_modelo, name='get_cilindradas'),
    path('api/anios/', views.get_anios_por_cilindrada, name='get_anios'),
    path('api/buscar-vehiculo/', views.buscar_productos_por_vehiculo, name='buscar_vehiculo'),
    
    # Panel de Administración
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/productos/', views.admin_productos, name='admin_productos'),
    path('panel/ventas/', views.admin_ventas, name='admin_ventas'),
    path('panel/compras/', views.admin_compras, name='admin_compras'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)