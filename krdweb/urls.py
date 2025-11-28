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
    # path("crearcompra/", views.addCompra, name="crear_compra"),
    path('vehiculos/agregar/', views.agregar_vehiculos, name='agregar_vehiculos'),
    path('vehiculos/lista/', views.lista_vehiculo, name='lista_vehiculo'),
    path('vehiculos/eliminar/<int:pk>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    path('catalogo/<uuid:id>/editar/', views.editProducto, name='editar_producto'),
    path('imagen/eliminar/<int:imagen_id>/', views.eliminar_imagen, name='eliminar_imagen'),
    path('imagen/principal/<int:imagen_id>/', views.cambiar_principal, name='cambiar_principal'),
    path('catalogo/<uuid:id>/sprite360/generar/', views.generar_sprite_360, name='generar_sprite_360'),
    path('catalogo/<uuid:id>/sprite360/eliminar/', views.eliminar_sprite_360, name='eliminar_sprite_360'),
    path('catalogo/<uuid:id>/eliminar/', views.eliminarProducto, name='eliminar_producto'),
    path('compras/crear/', views.addCompra, name='crear_compra'),
    # path('compras/', views.listar_compras, name='listar_compras'),
    path('carrito/', views.getCarrito, name='ver_carrito'),
    path('agregar/<uuid:producto_id>/', views.addCarrito, name='agregar_al_carrito'),
    path('quitar/<uuid:producto_id>/', views.eliminardelCarrito, name='remover_del_carrito'),
    path('actualizar/<uuid:producto_id>/', views.actualizarCantidadCarrito, name='actualizar_cantidad'),
    path('checkout/', views.procesarCompra, name='procesar_compra'),
    path('buscar-usuario/', views.buscar_usuario_rut, name='buscar_usuario_rut'),
    path('webpay/', views.webpay_iniciar, name='webpay_iniciar'),
    path('webpay/retorno/', views.webpay_retorno, name='webpay_retorno'),
    path('contador_carrito/', views.contador_carrito, name='contador_carrito'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    
    # API Filtro de Vehículos
    path('api/modelos/', views.get_modelos_por_marca, name='get_modelos'),
    path('api/cilindradas/', views.get_cilindradas_por_modelo, name='get_cilindradas'),
    path('api/anios/', views.get_anios_por_cilindrada, name='get_anios'),
    path('api/buscar-vehiculo/', views.buscar_productos_por_vehiculo, name='buscar_vehiculo'),
    path('api/debug-vehiculos/', views.debug_vehiculos, name='debug_vehiculos'),
    
    # API Filtro de Catálogo
    path('api/catalogo/modelos/', views.api_modelos_catalogo, name='api_modelos_catalogo'),
    path('api/catalogo/anios/', views.api_anios_catalogo, name='api_anios_catalogo'),
    
    # Panel de Administración
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/productos/', views.admin_productos, name='admin_productos'),
    path('panel/ventas/', views.admin_ventas, name='admin_ventas'),
    path('panel/compras/', views.admin_compras, name='admin_compras'),
    path('panel/logistica/', views.admin_logistica, name='admin_logistica'),
    path('panel/logistica/enviar/<int:venta_id>/', views.marcar_enviado, name='marcar_enviado'),
    path('panel/logistica/entregado/<int:venta_id>/', views.marcar_entregado, name='marcar_entregado'),
    path('panel/login/', views.panel_login, name='panel_login'),
    path('panel/logout/', views.panel_logout, name='panel_logout'),
    
    # Sistema de Valoraciones
    path('valorar/<int:venta_id>/', views.crear_valoracion, name='crear_valoracion'),
    path('valoracion/<int:venta_id>/', views.ver_valoracion, name='ver_valoracion'),
    path('opiniones/', views.valoraciones_publicas, name='valoraciones_publicas'),
    path('api/buscar-venta-valorar/', views.buscar_venta_valorar, name='buscar_venta_valorar'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)