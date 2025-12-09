from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, ProductoImagen, Compra, ProductoCompra, vehiculo, Producto_Vehiculo, Venta, Producto_Venta, Usuario, Logistica, Valoracion, Configuracion, Cupon
from .forms import ProductoForm, ProductoImagenForm, CompraForm, ProductoCompraForm, VehiculoForm, UsuarioForm
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from django.urls import reverse
import json, random, time
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from PIL import Image
import os
import tempfile
import shutil

# Webpay Transbank
from transbank.webpay.webpay_plus.transaction import Transaction

def home(request):
    # Obtener las marcas disponibles
    marcas = vehiculo.MARCAS
    # Obtener productos destacados desde Configuracion
    productos_destacados = Configuracion.get_productos_destacados()[:6]  # Máximo 6 productos
    
    return render(request, "public/home.html", {
        'marcas': marcas,
        'productos_destacados': productos_destacados,
    })


# API para filtro de vehículos
def get_modelos_por_marca(request):
    """Retorna los modelos disponibles para una marca específica"""
    marca = request.GET.get('marca', '')
    modelos = vehiculo.objects.filter(marca=marca).values_list('modelo', flat=True).distinct()
    return JsonResponse({'modelos': list(modelos)})

def get_cilindradas_por_modelo(request):
    """Retorna las cilindradas disponibles para una marca y modelo"""
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    cilindradas = vehiculo.objects.filter(marca=marca, modelo=modelo).values_list('cilindrada', flat=True).distinct()
    return JsonResponse({'cilindradas': [str(c) for c in cilindradas]})

def get_anios_por_cilindrada(request):
    """Retorna los años disponibles para una marca, modelo y cilindrada"""
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    cilindrada = request.GET.get('cilindrada', '')
    anios = vehiculo.objects.filter(marca=marca, modelo=modelo, cilindrada=cilindrada).values_list('anio', flat=True).distinct().order_by('anio')
    return JsonResponse({'anios': list(anios)})

def buscar_productos_por_vehiculo(request):
    """Busca productos compatibles con el vehículo seleccionado"""
    marca = request.GET.get('marca', '').strip()
    modelo = request.GET.get('modelo', '').strip()
    cilindrada = request.GET.get('cilindrada', '').strip()
    anio = request.GET.get('anio', '').strip()
    
    # Buscar el vehículo
    vehiculos_encontrados = vehiculo.objects.filter(
        marca__iexact=marca,
        modelo__iexact=modelo,
        cilindrada=float(cilindrada) if cilindrada else None,
        anio=int(anio) if anio else None
    )
    
    if vehiculos_encontrados.exists():
        # Obtener productos compatibles
        productos_ids = Producto_Vehiculo.objects.filter(
            vehiculo__in=vehiculos_encontrados
        ).values_list('producto_id', flat=True).distinct()
        
        if productos_ids:
            productos_ids_str = ",".join(str(p) for p in productos_ids)
            return JsonResponse({
                'success': True,
                'redirect_url': f'/catalogo/?vehiculo_ids={productos_ids_str}',
                'debug': {
                    'vehiculos_encontrados': vehiculos_encontrados.count(),
                    'productos_encontrados': len(productos_ids)
                }
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'No hay productos asociados al vehículo especificado'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'No hay productos asociados al vehículo especificado'
    })


def debug_vehiculos(request):
    """Vista de diagnóstico para verificar datos de vehículos y productos"""
    from django.db.models import Count
    
    # Contar datos
    total_vehiculos = vehiculo.objects.count()
    total_productos = Producto.objects.count()
    total_asociaciones = Producto_Vehiculo.objects.count()
    
    # Vehículos con productos asociados
    vehiculos_con_productos = vehiculo.objects.annotate(
        productos_count=Count('producto_vehiculo')
    ).filter(productos_count__gt=0).count()
    
    # Productos sin asociación
    productos_sin_asociacion = Producto.objects.annotate(
        asociaciones=Count('producto_vehiculo')
    ).filter(asociaciones=0).count()
    
    # Primeros 10 vehículos
    primeros_vehiculos = list(
        vehiculo.objects.values('marca', 'modelo', 'cilindrada', 'anio')[:10]
    )
    
    # Primeros 10 asociaciones
    primeras_asociaciones = list(
        Producto_Vehiculo.objects.select_related('vehiculo', 'producto').values(
            'vehiculo__marca', 'vehiculo__modelo', 'producto__n_producto'
        )[:10]
    )
    
    return JsonResponse({
        'total_vehiculos': total_vehiculos,
        'total_productos': total_productos,
        'total_asociaciones': total_asociaciones,
        'vehiculos_con_productos': vehiculos_con_productos,
        'productos_sin_asociacion': productos_sin_asociacion,
        'primeros_vehiculos': primeros_vehiculos,
        'primeras_asociaciones': primeras_asociaciones
    }, indent=2)

def sobre_nosotros(request):
    return render(request, 'public/sobre_nosotros.html', {})

####OPTIMIZACION IMAGENES
def crear_sprite_360(imagenes_paths, producto_id, img_deseadas=36):
    """
    Combina múltiples imágenes en un sprite sheet para vista 360°
    
    Args:
        imagenes_paths: Lista de rutas a las imágenes
        producto_id: ID del producto
        img_deseadas: Número de imágenes a incluir (default 36)
    
    Returns:
        Tupla: (ruta_relativa_sprite, columnas, filas, total_imagenes)
    """
    total_imagenes = len(imagenes_paths)
    
    # Seleccionar imágenes uniformemente distribuidas
    if total_imagenes > img_deseadas:
        paso = total_imagenes / img_deseadas
        indices = [int(i * paso) for i in range(img_deseadas)]
        imagenes_seleccionadas = [imagenes_paths[i] for i in indices if i < total_imagenes]
    else:
        imagenes_seleccionadas = imagenes_paths
        img_deseadas = len(imagenes_seleccionadas)
    
    # Calcular grilla óptima (6x6 para 36 imágenes)
    columnas = 6
    filas = (img_deseadas + columnas - 1) // columnas  # Redondear hacia arriba
    
    # Abrir primera imagen para obtener dimensiones
    primera = Image.open(imagenes_seleccionadas[0])
    
    # Redimensionar a un tamaño estándar (400x400 para balance calidad/peso)
    ancho_frame = 400
    alto_frame = 400
    
    # Crear lienzo del sprite
    sprite_ancho = ancho_frame * columnas
    sprite_alto = alto_frame * filas
    sprite = Image.new('RGB', (sprite_ancho, sprite_alto), (255, 255, 255))
    
    # Pegar cada imagen en su posición
    for i, img_path in enumerate(imagenes_seleccionadas):
        try:
            img = Image.open(img_path)
            
            # Redimensionar manteniendo aspecto y recortando al centro
            img = img.convert('RGB')
            
            # Calcular ratio para cubrir el frame
            ratio_w = ancho_frame / img.width
            ratio_h = alto_frame / img.height
            ratio = max(ratio_w, ratio_h)
            
            nuevo_ancho = int(img.width * ratio)
            nuevo_alto = int(img.height * ratio)
            img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            # Recortar al centro
            left = (nuevo_ancho - ancho_frame) // 2
            top = (nuevo_alto - alto_frame) // 2
            img = img.crop((left, top, left + ancho_frame, top + alto_frame))
            
            # Calcular posición en el sprite
            columna = i % columnas
            fila = i // columnas
            x = columna * ancho_frame
            y = fila * alto_frame
            
            # Pegar en el sprite
            sprite.paste(img, (x, y))
            
        except Exception as e:
            print(f"Error procesando imagen {i}: {e}")
            continue
    
    # Crear directorio de sprites si no existe
    sprites_dir = os.path.join(settings.MEDIA_ROOT, 'sprites')
    os.makedirs(sprites_dir, exist_ok=True)
    
    # Guardar sprite con compresión
    sprite_filename = f'sprite_360_{producto_id}.jpg'
    sprite_path = os.path.join(sprites_dir, sprite_filename)
    sprite.save(sprite_path, 'JPEG', quality=85, optimize=True)
    
    # Retornar ruta relativa para el modelo
    return (f'sprites/{sprite_filename}', columnas, filas, len(imagenes_seleccionadas))


def addProducto(request):
    if request.method == "POST":
        form_producto = ProductoForm(request.POST)
        form_imagenes = ProductoImagenForm(request.POST, request.FILES or None)

        if form_producto.is_valid():
            producto = form_producto.save()
            imagenes = request.FILES.getlist('imagenes')
            principal_idx = int(request.POST.get('principal_idx', 0))
            
            # Obtener el checkbox es_360
            es_360 = request.POST.get('es_360') == 'true'
            
            print(f"DEBUG: es_360={es_360}, total_imagenes={len(imagenes)}")
            
            if es_360 and len(imagenes) >= 1:
                # Crear directorio temporal para las imágenes
                temp_dir = tempfile.mkdtemp()
                
                try:
                    # Guardar imágenes temporalmente
                    imagenes_paths = []
                    for i, img in enumerate(imagenes):
                        ruta_temp = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                        with open(ruta_temp, 'wb+') as destination:
                            for chunk in img.chunks():
                                destination.write(chunk)
                        imagenes_paths.append(ruta_temp)
                    
                    # Crear el sprite
                    sprite_path, cols, rows, total = crear_sprite_360(
                        imagenes_paths, 
                        producto.id_producto,
                        img_deseadas=36
                    )
                    
                    # Actualizar producto con datos del sprite
                    producto.sprite_360 = sprite_path
                    producto.sprite_cols = cols
                    producto.sprite_rows = rows
                    producto.sprite_total = total
                    producto.save()
                    
                    # También guardar la primera imagen como imagen principal para el catálogo
                    if imagenes:
                        ProductoImagen.objects.create(
                            producto=producto,
                            imagen=imagenes[0],
                            es_principal=True,
                            es_360=False
                        )
                    
                    messages.success(request, f"Producto creado con sprite 360° ({total} frames)")
                    
                finally:
                    # Limpiar temporales
                    shutil.rmtree(temp_dir)
                    
            else:
                # Proceso normal para imágenes no-360
                for i, img in enumerate(imagenes):
                    ProductoImagen.objects.create(
                        producto=producto,
                        imagen=img,
                        es_principal=True if i == principal_idx else False,
                        es_360=False
                    )
                messages.success(request, "Producto creado con éxito")

            return redirect("/catalogo/")
        else:
            print("error prod:", form_producto.errors)
            print("error img:", form_imagenes.errors)
            messages.error(request, "Error al crear el producto")
            return render(request, "productos/crear.html", {
                "form_producto": form_producto, 
                "form_imagenes": form_imagenes
            })
    else:
        form_producto = ProductoForm()
        form_imagenes = ProductoImagenForm()
        return render(request, "productos/crear.html", {
            "form_producto": form_producto, 
            "form_imagenes": form_imagenes
        })
     
def addCompra(request):
    if request.method == "POST":
        form = CompraForm(request.POST, request.FILES)
        productos_data = json.loads(request.POST.get("productos_data", "[]"))

        if form.is_valid():
            compra = form.save(commit=False)
            compra.subtotalc = 0
            compra.save()

            subtotal_total = 0
            for p in productos_data:
                prod = Producto.objects.get(id_producto=p["producto"])
                cantidad = int(p["cantidad"])
                precio = Decimal(p["precio"])
                pc = ProductoCompra.objects.create(
                    compra=compra,
                    producto=prod,
                    cantidad_compra=cantidad,
                    precio_und=precio
                )
                prod.stock += cantidad
                prod.save()
                subtotal_total += pc.subtotal_prod

            compra.subtotalc = subtotal_total
            compra.save()

            return redirect("admin_compras")
    else:
        form = CompraForm()

    return render(request, "compras/crear.html", {
        "form": form,
        "productos": Producto.objects.all()
    })

def agregar_vehiculos(request):
    """Redirige a la lista de vehículos (ahora todo está en una sola página)"""
    return redirect('lista_vehiculo')

def lista_vehiculo(request):
    """Lista de vehículos con formulario de agregar integrado"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    if request.method == 'POST':
        # Crear vehículo desde el modal
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        cilindrada = request.POST.get('cilindrada')
        anio = request.POST.get('anio')
        
        if marca and modelo and cilindrada and anio:
            vehiculo.objects.create(
                marca=marca,
                modelo=modelo,
                cilindrada=cilindrada,
                anio=anio
            )
            messages.success(request, f'Vehículo {marca} {modelo} agregado correctamente')
        return redirect('lista_vehiculo')
    
    vehiculos = vehiculo.objects.all().order_by('marca', 'modelo', '-anio')
    return render(request, 'panel/vehiculos.html', {'vehiculos': vehiculos})

def eliminar_vehiculo(request, pk):
    veh = get_object_or_404(vehiculo, pk=pk)
    if request.method == "POST":
        veh.delete()
        return redirect('lista_vehiculo')
    return render(request, 'krd/confirmar_eliminacion.html', {'vehiculo': veh})

def addCarrito(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    carrito = request.session.get('carrito', {})
    cantidad = 4  # Por defecto 4 unidades
    try:
        cantidad = int(request.GET.get('cantidad', '4'))
        # Asegurar que sea múltiplo de 4
        if cantidad < 4:
            cantidad = 4
        elif cantidad % 4 != 0:
            cantidad = ((cantidad // 4) + 1) * 4  # Redondear al siguiente múltiplo de 4
    except Exception:
        cantidad = 4

    id_str = str(producto_id)
    if id_str in carrito:
        nueva_cantidad = carrito[id_str]['cantidad'] + cantidad
        # Asegurar que la cantidad total sea múltiplo de 4
        if nueva_cantidad % 4 != 0:
            nueva_cantidad = ((nueva_cantidad // 4) + 1) * 4
        carrito[id_str]['cantidad'] = nueva_cantidad
        carrito[id_str]['subtotal'] = carrito[id_str]['cantidad'] * carrito[id_str]['precio']
    else:
        carrito[id_str] = {
            'nombre': producto.n_producto,
            'precio': producto.precio,
            'cantidad': cantidad,
            'subtotal': producto.precio * cantidad
        }
    request.session['carrito'] = carrito
    request.session.modified = True
    # Redirigir de vuelta a la página del producto con mensaje de éxito
    return redirect(f"/catalogo/{producto_id}?mensaje=ok")

# def buscarCliente(request):
#     rut = request.GET.get("rut")
#     try:
#         usuario = Usuario.objects.get(rut=rut)
        
#         codigo = str(random.randint(100000, 999999))
#         cod_encriptado = make_password(codigo)
#         generadoa= int(time.time()) ##minuto en el cual fue generado

#         request.session['cod_encriptado'] = cod_encriptado
#         request.session['cod_generadoa'] = generadoa
#         request.session['rut_usuario'] = rut

#         send_mail(
#             'Código de verificación',
#             f'¡Hola, solo queremos asegurarnos que eres tú!😁 \n Tu código de verificación es: {codigo}\nExpira en 5 minutos.',
#             settings.DEFAULT_FROM_EMAIL,
#             [usuario.email],
#             fail_silently=False,
#         )
#         return JsonResponse({"existe"})


### SECCION GET (MODELS)
def getCatalogo(request):
    if request.method=="GET":
        prods = Producto.objects.all()
        filtrado_vehiculo = False
        filtros_activos = {}
        
        # Filtro por vehículo (desde home)
        vehiculo_ids = request.GET.get('vehiculo_ids', '')
        if vehiculo_ids:
            try:
                producto_ids = [pid.strip() for pid in vehiculo_ids.split(',') if pid.strip()]
                if producto_ids:
                    prods = prods.filter(id_producto__in=producto_ids)
                    filtrado_vehiculo = True
            except Exception as e:
                print(f"Error al filtrar productos: {e}")
        
        # Filtros por especificaciones técnicas
        aro = request.GET.get('aro', '')
        if aro:
            prods = prods.filter(aro=int(aro))
            filtros_activos['aro'] = aro
            
        ancho = request.GET.get('ancho', '')
        if ancho:
            prods = prods.filter(ancho=ancho)
            filtros_activos['ancho'] = ancho
            
        apernadura = request.GET.get('apernadura', '')
        if apernadura:
            prods = prods.filter(apernadura=apernadura)
            filtros_activos['apernadura'] = apernadura
            
        offset = request.GET.get('offset', '')
        if offset:
            prods = prods.filter(offset=int(offset))
            filtros_activos['offset'] = offset
            
        centro = request.GET.get('centro', '')
        if centro:
            prods = prods.filter(centro_llanta=centro)
            filtros_activos['centro'] = centro
        
        # Filtro por marca de vehículo compatible
        marca_vehiculo = request.GET.get('marca_vehiculo', '')
        if marca_vehiculo:
            producto_ids = Producto_Vehiculo.objects.filter(
                vehiculo__marca__iexact=marca_vehiculo
            ).values_list('producto_id', flat=True).distinct()
            prods = prods.filter(id_producto__in=producto_ids)
            filtros_activos['marca_vehiculo'] = marca_vehiculo
            
        # Filtro por modelo de vehículo compatible
        modelo_vehiculo = request.GET.get('modelo_vehiculo', '')
        if modelo_vehiculo:
            producto_ids = Producto_Vehiculo.objects.filter(
                vehiculo__modelo__iexact=modelo_vehiculo
            ).values_list('producto_id', flat=True).distinct()
            prods = prods.filter(id_producto__in=producto_ids)
            filtros_activos['modelo_vehiculo'] = modelo_vehiculo
            
        # Filtro por año de vehículo compatible
        anio_vehiculo = request.GET.get('anio_vehiculo', '')
        if anio_vehiculo:
            producto_ids = Producto_Vehiculo.objects.filter(
                vehiculo__anio=int(anio_vehiculo)
            ).values_list('producto_id', flat=True).distinct()
            prods = prods.filter(id_producto__in=producto_ids)
            filtros_activos['anio_vehiculo'] = anio_vehiculo
        
        # Obtener opciones para los filtros
        marcas_vehiculo = vehiculo.MARCAS
        todos_productos = Producto.objects.all()
        aros_disponibles = sorted(todos_productos.values_list('aro', flat=True).distinct())
        anchos_disponibles = sorted(todos_productos.values_list('ancho', flat=True).distinct())
        apernaduras_disponibles = sorted(todos_productos.values_list('apernadura', flat=True).distinct())
        offsets_disponibles = sorted(todos_productos.values_list('offset', flat=True).distinct())
        centros_disponibles = sorted(todos_productos.values_list('centro_llanta', flat=True).distinct())
        
        # Lista de años fija de 2025 a 1990
        anios_disponibles = list(range(2025, 1989, -1))
        
        # Umbral de bajo stock desde configuración
        umbral_bajo_stock = int(Configuracion.get_valor('umbral_bajo_stock', '5'))
        
        # IDs de productos destacados para marcarlos en el catálogo
        productos_destacados_ids = [str(p.id_producto) for p in Configuracion.get_productos_destacados()]
            
        return render(request, "productos/catalogo.html", {
            "prods": prods, 
            "filtrado_vehiculo": filtrado_vehiculo,
            "filtros_activos": filtros_activos,
            "total_productos": prods.count(),
            "umbral_bajo_stock": umbral_bajo_stock,
            "productos_destacados_ids": productos_destacados_ids,
            # Opciones de filtros
            "marcas_vehiculo": marcas_vehiculo,
            "aros_disponibles": aros_disponibles,
            "anchos_disponibles": anchos_disponibles,
            "apernaduras_disponibles": apernaduras_disponibles,
            "offsets_disponibles": offsets_disponibles,
            "centros_disponibles": centros_disponibles,
            "anios_disponibles": anios_disponibles,
        })


# APIs para filtros dinámicos del catálogo
def api_modelos_catalogo(request):
    """Retorna los modelos de vehículos para una marca (para filtro del catálogo)"""
    marca = request.GET.get('marca', '')
    if marca:
        modelos = vehiculo.objects.filter(marca__iexact=marca).values_list('modelo', flat=True).distinct()
        return JsonResponse({'modelos': sorted(list(set(modelos)))})
    return JsonResponse({'modelos': []})

def api_anios_catalogo(request):
    """Retorna los años disponibles para marca/modelo (para filtro del catálogo)"""
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    
    qs = vehiculo.objects.all()
    if marca:
        qs = qs.filter(marca__iexact=marca)
    if modelo:
        qs = qs.filter(modelo__iexact=modelo)
    
    anios = qs.values_list('anio', flat=True).distinct()
    return JsonResponse({'anios': sorted(list(set(anios)))})
    

def getProducto(request, id):
    if request.method == "GET":
        prod = Producto.objects.get(id_producto=id)
        imgprod = prod.imagenes.all()
        
        # Obtener vehículos compatibles
        vehiculos_compatibles = Producto_Vehiculo.objects.filter(producto=prod).select_related('vehiculo')
        
        # Verificar si tiene sprite 360 (nueva forma optimizada)
        sprite_360_data = None
        if prod.sprite_360:
            sprite_360_data = {
                'url': request.build_absolute_uri(prod.sprite_360.url),
                'cols': prod.sprite_cols,
                'rows': prod.sprite_rows,
                'total': prod.sprite_total
            }
        
        return render(request, "productos/detalle.html", {
            "prod": prod, 
            "imgs": imgprod.filter(es_360=False),  # Solo imágenes normales
            "sprite_360_data": json.dumps(sprite_360_data) if sprite_360_data else None,
            "vehiculos_compatibles": vehiculos_compatibles,
        })
    

def getCarrito(request):
    carrito = request.session.get('carrito', {})
    subtotal = sum(item['subtotal'] for item in carrito.values())
    
    # Verificar si hay cupón aplicado
    cupon_aplicado = None
    descuento = 0
    cupon_codigo = request.session.get('cupon_codigo')
    
    if cupon_codigo:
        try:
            cupon = Cupon.objects.get(codigo=cupon_codigo, activo=True)
            if cupon.es_valido():
                cupon_aplicado = cupon
                if cupon.tipo == 'porcentaje':
                    descuento = int(subtotal * cupon.valor / 100)
                else:  # monto fijo
                    descuento = int(cupon.valor)
                    if descuento > subtotal:
                        descuento = subtotal
            else:
                # Cupón expirado o sin usos, remover de sesión
                del request.session['cupon_codigo']
                request.session.modified = True
        except Cupon.DoesNotExist:
            del request.session['cupon_codigo']
            request.session.modified = True
    
    total = subtotal - descuento
    
    return render(request, 'carrito/carrito.html', {
        'carrito': carrito, 
        'subtotal': subtotal,
        'total': total,
        'cupon_aplicado': cupon_aplicado,
        'descuento': descuento,
    })


def aplicar_cupon(request):
    """Aplica un cupón de descuento al carrito"""
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        
        if not codigo:
            messages.error(request, 'Ingresa un código de cupón')
            return redirect('carrito')
        
        try:
            cupon = Cupon.objects.get(codigo=codigo)
            
            if not cupon.activo:
                messages.error(request, 'Este cupón no está activo')
                return redirect('carrito')
            
            if not cupon.es_valido():
                if cupon.usos_actuales >= cupon.usos_maximos:
                    messages.error(request, 'Este cupón ha alcanzado el límite de usos')
                else:
                    messages.error(request, 'Este cupón ha expirado')
                return redirect('carrito')
            
            # Aplicar cupón
            request.session['cupon_codigo'] = codigo
            request.session.modified = True
            messages.success(request, f'¡Cupón "{codigo}" aplicado correctamente!')
            
        except Cupon.DoesNotExist:
            messages.error(request, 'Cupón no válido')
        
        return redirect('carrito')
    
    return redirect('carrito')


def remover_cupon(request):
    """Remueve el cupón aplicado del carrito"""
    if 'cupon_codigo' in request.session:
        del request.session['cupon_codigo']
        request.session.modified = True
        messages.success(request, 'Cupón removido')
    return redirect('carrito')

###SECCION DE EDITS

def editProducto(request, id):
    prod = get_object_or_404(Producto, id_producto=id)
    imgs = prod.imagenes.all()
    vehiculos = vehiculo.objects.all()
    # Obtener vehículos asociados para inicializar el JS
    vehiculos_asociados_qs = Producto_Vehiculo.objects.filter(producto=prod).select_related('vehiculo')
    vehiculos_asociados = [
        {
            'id': str(vv.vehiculo.id),
            'text': f"{vv.vehiculo.marca}, {vv.vehiculo.modelo}, {vv.vehiculo.cilindrada}, {vv.vehiculo.anio}"
        }
        for vv in vehiculos_asociados_qs
    ]
    if request.method == "POST":
        form_producto = ProductoForm(request.POST, instance=prod)
        if form_producto.is_valid():
            producto = form_producto.save()
            # Guardar nuevas imágenes si se subieron
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                ProductoImagen.objects.create(
                    producto=producto,
                    imagen=img,
                    es_principal=False
                )
            # Guardar aplicaciones del producto (vehículos asociados)
            vehiculos_ids = request.POST.get('vehiculos_ids', '')
            # Eliminar relaciones previas
            Producto_Vehiculo.objects.filter(producto=producto).delete()
            # Crear nuevas relaciones
            if vehiculos_ids:
                for v_id in vehiculos_ids.split(','):
                    if v_id:
                        Producto_Vehiculo.objects.create(producto=producto, vehiculo_id=v_id)
            messages.success(request, "Producto editado con éxito")
            return redirect("/catalogo/")
        else:
            from django.contrib import messages as dj_messages
            return render(request, "productos/editar.html", {
                "form_producto": form_producto,
                "form_imagenes": ProductoImagenForm(),
                "prod": prod,
                "imgs": imgs,
                "vehiculos": vehiculos,
                "vehiculos_asociados": vehiculos_asociados,
                "vehiculos_asociados_json": json.dumps(vehiculos_asociados),
                "messages": dj_messages.get_messages(request)
            })
    else:
        form_producto = ProductoForm(instance=prod)
        from django.contrib import messages as dj_messages
        return render(request, "productos/editar.html", {
            "form_producto": form_producto,
            "form_imagenes": ProductoImagenForm(),
            "prod": prod,
            "imgs": imgs,
            "vehiculos": vehiculos,
            "vehiculos_asociados": vehiculos_asociados,
            "vehiculos_asociados_json": json.dumps(vehiculos_asociados),
            "messages": dj_messages.get_messages(request)
        })

def cambiar_principal(request, imagen_id):
    imagen = get_object_or_404(ProductoImagen, id=imagen_id)
    producto = imagen.producto
    if request.method == "POST":
        # Desmarcar todas las imágenes como principal
        ProductoImagen.objects.filter(producto=producto).update(es_principal=False)
        # Marcar la seleccionada como principal
        imagen.es_principal = True
        imagen.save()
        messages.success(request, "Imagen principal actualizada.")
        return redirect(reverse('editar_producto', args=[producto.id_producto]))
    return HttpResponse("Método no permitido", status=405)

def eliminar_imagen(request, imagen_id):
    imagen = get_object_or_404(ProductoImagen, id=imagen_id)
    producto_id = imagen.producto.id_producto
    if request.method == "POST":
        imagen.delete()
        messages.success(request, "Imagen eliminada correctamente.")
        return redirect(reverse('editar_producto', args=[producto_id]))
    return HttpResponse("Método no permitido", status=405)


def generar_sprite_360(request, id):
    """Generar o regenerar sprite 360° para un producto"""
    producto = get_object_or_404(Producto, id_producto=id)
    
    if request.method == "POST":
        imagenes = request.FILES.getlist('imagenes_360')
        
        if not imagenes or len(imagenes) < 2:
            messages.error(request, "Debes subir al menos 2 imágenes para crear el sprite 360°")
            return redirect(reverse('editar_producto', args=[id]))
        
        # Crear directorio temporal para las imágenes
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Guardar imágenes temporalmente
            imagenes_paths = []
            for i, img in enumerate(imagenes):
                ruta_temp = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                with open(ruta_temp, 'wb+') as destination:
                    for chunk in img.chunks():
                        destination.write(chunk)
                imagenes_paths.append(ruta_temp)
            
            # Eliminar sprite anterior si existe
            if producto.sprite_360:
                try:
                    old_sprite_path = os.path.join(settings.MEDIA_ROOT, str(producto.sprite_360))
                    if os.path.exists(old_sprite_path):
                        os.remove(old_sprite_path)
                except Exception as e:
                    print(f"Error eliminando sprite anterior: {e}")
            
            # Crear el sprite
            sprite_path, cols, rows, total = crear_sprite_360(
                imagenes_paths, 
                producto.id_producto,
                img_deseadas=36
            )
            
            # Actualizar producto con datos del sprite
            producto.sprite_360 = sprite_path
            producto.sprite_cols = cols
            producto.sprite_rows = rows
            producto.sprite_total = total
            producto.save()
            
            messages.success(request, f"Sprite 360° generado exitosamente ({total} frames)")
            
        except Exception as e:
            messages.error(request, f"Error al generar sprite: {str(e)}")
        finally:
            # Limpiar temporales
            shutil.rmtree(temp_dir)
        
        return redirect(reverse('editar_producto', args=[id]))
    
    return HttpResponse("Método no permitido", status=405)


def eliminar_sprite_360(request, id):
    """Eliminar sprite 360° de un producto"""
    producto = get_object_or_404(Producto, id_producto=id)
    
    if request.method == "POST":
        if producto.sprite_360:
            try:
                # Eliminar archivo físico
                sprite_path = os.path.join(settings.MEDIA_ROOT, str(producto.sprite_360))
                if os.path.exists(sprite_path):
                    os.remove(sprite_path)
            except Exception as e:
                print(f"Error eliminando archivo: {e}")
            
            # Limpiar campos del modelo
            producto.sprite_360 = None
            producto.sprite_cols = 6
            producto.sprite_rows = 6
            producto.sprite_total = 36
            producto.save()
            
            messages.success(request, "Sprite 360° eliminado. El producto mostrará las imágenes normales.")
        else:
            messages.warning(request, "Este producto no tiene sprite 360°")
        
        return redirect(reverse('editar_producto', args=[id]))
    
    return HttpResponse("Método no permitido", status=405)


##Seccion Eliminar

def eliminarProducto(request, id):
    prod = get_object_or_404(Producto, id_producto=id)
    if request.method == "POST":
        prod.delete()
        messages.success(request, "Producto eliminado con éxito")
        return redirect("/catalogo/")
    
def eliminardelCarrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    id_str = str(producto_id)
    if id_str in carrito:
        del carrito[id_str]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, "Producto eliminado del carrito.")
    return redirect('/catalogo/')

def actualizarCantidadCarrito(request, producto_id):
    """Actualiza la cantidad de un producto en el carrito"""
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        id_str = str(producto_id)
        
        if id_str in carrito:
            try:
                nueva_cantidad = int(request.POST.get('cantidad', 4))
                
                # Validar que sea múltiplo de 4
                if nueva_cantidad % 4 != 0:
                    nueva_cantidad = (nueva_cantidad // 4) * 4
                    if nueva_cantidad < 4:
                        nueva_cantidad = 4
                
                # Validar stock disponible
                try:
                    producto = Producto.objects.get(id_producto=producto_id)
                    if nueva_cantidad > producto.stock:
                        messages.error(request, f"Stock insuficiente. Disponible: {producto.stock}")
                        return redirect('ver_carrito')
                except Producto.DoesNotExist:
                    messages.error(request, "Producto no encontrado.")
                    return redirect('ver_carrito')
                
                if nueva_cantidad <= 0:
                    # Si la cantidad es 0 o negativa, eliminar del carrito
                    del carrito[id_str]
                    messages.success(request, "Producto eliminado del carrito.")
                else:
                    carrito[id_str]['cantidad'] = nueva_cantidad
                    carrito[id_str]['subtotal'] = carrito[id_str]['precio'] * nueva_cantidad
                    messages.success(request, "Cantidad actualizada.")
                
                request.session['carrito'] = carrito
                request.session.modified = True
            except ValueError:
                messages.error(request, "Cantidad inválida.")
    
    return redirect('ver_carrito')


### SECCION CONTROL DE STOCK Y SEGURIDAD
def procesarCompra(request):
    """Muestra el formulario de checkout y guarda datos del cliente en sesión (NO crea Venta aún)"""
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect("ver_carrito")
    
    # Validar que todas las cantidades sean múltiplos de 4
    for id_producto, item in carrito.items():
        if item['cantidad'] % 4 != 0:
            messages.error(request, f"La cantidad de {item['nombre']} debe ser múltiplo de 4.")
            return redirect("ver_carrito")
    
    # Validar stock disponible antes de mostrar checkout
    for id_producto, item in carrito.items():
        try:
            producto = Producto.objects.get(id_producto=id_producto)
            if producto.stock < item['cantidad']:
                messages.error(request, f"No hay suficiente stock para {item['nombre']}. Stock disponible: {producto.stock}")
                return redirect("ver_carrito")
        except Producto.DoesNotExist:
            messages.error(request, f"El producto {item['nombre']} ya no está disponible.")
            return redirect("ver_carrito")
    
    subtotal = sum(item['subtotal'] for item in carrito.values())
    
    # Calcular descuento por cupón
    cupon_aplicado = None
    descuento = 0
    cupon_codigo = request.session.get('cupon_codigo')
    
    if cupon_codigo:
        try:
            cupon = Cupon.objects.get(codigo=cupon_codigo, activo=True)
            if cupon.es_valido():
                cupon_aplicado = cupon
                if cupon.tipo == 'porcentaje':
                    descuento = int(subtotal * cupon.valor / 100)
                else:
                    descuento = int(cupon.valor)
                    if descuento > subtotal:
                        descuento = subtotal
            else:
                del request.session['cupon_codigo']
                request.session.modified = True
        except Cupon.DoesNotExist:
            del request.session['cupon_codigo']
            request.session.modified = True
    
    total = subtotal - descuento
    
    if request.method == 'POST':
        # Capturar datos del formulario
        rut = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        
        # Validar campos requeridos
        if not all([rut, nombre, apellido, email, telefono, direccion]):
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'checkout.html', {
                'carrito': carrito,
                'subtotal': subtotal,
                'total': total,
                'cupon_aplicado': cupon_aplicado,
                'descuento': descuento,
                'datos': request.POST
            })
        
        # Guardar datos del cliente en sesión (NO crear Venta aún)
        # La Venta se creará SOLO cuando el pago sea exitoso en webpay_retorno
        request.session['cliente_temp'] = {
            'rut': rut,
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'telefono': telefono,
            'direccion': direccion,
        }
        request.session['total_venta'] = int(total)
        request.session['descuento_aplicado'] = descuento
        request.session['cupon_usado'] = cupon_codigo if cupon_aplicado else None
        request.session.modified = True
        
        # Redirigir a Webpay
        return redirect('webpay_iniciar')
    
    return render(request, 'checkout.html', {
        'carrito': carrito,
        'subtotal': subtotal,
        'total': total,
        'cupon_aplicado': cupon_aplicado,
        'descuento': descuento,
    })


def buscar_usuario_rut(request):
    """API para buscar usuario por RUT y autocompletar datos"""
    rut = request.GET.get('rut', '').strip()
    if not rut:
        return JsonResponse({'found': False})
    
    try:
        usuario = Usuario.objects.get(rut=rut)
        return JsonResponse({
            'found': True,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'email': usuario.email,
            'telefono': str(usuario.telefono),
            'direccion': usuario.direccion,
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'found': False})


def webpay_iniciar(request):
    """Inicia la transacción con Webpay Plus"""
    cliente_temp = request.session.get('cliente_temp')
    total = request.session.get('total_venta')
    carrito = request.session.get('carrito', {})
    
    if not cliente_temp or not total or not carrito:
        messages.error(request, "No hay datos de compra pendiente.")
        return redirect('ver_carrito')
    
    try:
        # Credenciales de integración (prueba) de Transbank
        COMMERCE_CODE = "597055555532"
        API_KEY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
        
        # Usar credenciales de producción si están configuradas
        if getattr(settings, 'WEBPAY_PRODUCTION', False):
            tx = Transaction.build_for_production(
                settings.WEBPAY_COMMERCE_CODE,
                settings.WEBPAY_API_KEY
            )
        else:
            tx = Transaction.build_for_integration(COMMERCE_CODE, API_KEY)
        
        timestamp = int(time.time())
        buy_order = f"orden_{timestamp}"
        session_id = f"sesion_{timestamp}"
        amount = int(total)  
        

        return_url = request.build_absolute_uri(reverse('webpay_retorno'))

        response = tx.create(buy_order, session_id, amount, return_url)
        
        # Guardar token en sesión para validación posterior
        request.session['webpay_token'] = response['token']
        request.session['webpay_buy_order'] = buy_order
        request.session.modified = True
        
        # Redirigir directamente a Webpay (agregar token como parámetro GET)
        webpay_url = f"{response['url']}?token_ws={response['token']}"
        return redirect(webpay_url)
        
    except Exception as e:
        messages.error(request, f"Error al conectar con Webpay: {str(e)}")
        return redirect('ver_carrito')


def webpay_retorno(request):
    """Procesa el retorno de Webpay --- CREA la Venta SOLO si el pago es exitoso"""
    # Obtener token de la respuesta (puede venir por GET o POST)
    token = request.GET.get('token_ws') or request.POST.get('token_ws')
    
    # Si el usuario canceló el pago (TBK_TOKEN indica cancelación)
    if request.GET.get('TBK_TOKEN') or not token:
        # Limpiar datos temporales de sesión (el carrito se mantiene)
        for key in ['cliente_temp', 'total_venta', 'webpay_token', 'webpay_buy_order']:
            request.session.pop(key, None)
        request.session.modified = True
        
        messages.warning(request, "El pago fue cancelado. Tu carrito sigue disponible.")
        return redirect('ver_carrito')
    
    try:
        # Credenciales de integración (prueba) de Transbank
        COMMERCE_CODE = "597055555532"
        API_KEY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
        
        if getattr(settings, 'WEBPAY_PRODUCTION', False):
            tx = Transaction.build_for_production(
                settings.WEBPAY_COMMERCE_CODE,
                settings.WEBPAY_API_KEY
            )
        else:
            tx = Transaction.build_for_integration(COMMERCE_CODE, API_KEY)
        
        # Confirmar transacción - devuelve un diccionario
        response = tx.commit(token)
        
        cliente_temp = request.session.get('cliente_temp')
        total = request.session.get('total_venta')
        carrito = request.session.get('carrito', {})
        
        # Verificar que el pago fue exitoso
        if response.get('status') == 'AUTHORIZED' and response.get('response_code') == 0:
            # PAGO EXITOSO - AHORA crear Usuario, Venta, Producto_Venta, descontar stock
            try:
                with transaction.atomic():
                    # Crear o actualizar usuario
                    usuario, created = Usuario.objects.update_or_create(
                        rut=cliente_temp['rut'],
                        defaults={
                            'nombre': cliente_temp['nombre'],
                            'apellido': cliente_temp['apellido'],
                            'email': cliente_temp['email'],
                            'telefono': int(cliente_temp['telefono']),
                            'direccion': cliente_temp['direccion'],
                        }
                    )
                    
                    # Crear la venta
                    venta = Venta.objects.create(
                        id_usuario=cliente_temp['rut'],
                        precio_venta=total,
                    )
                    
                    # Crear productos de la venta Y descontar stock
                    for id_producto, item in carrito.items():
                        producto = Producto.objects.select_for_update().get(id_producto=id_producto)
                        
                        if producto.stock < item['cantidad']:
                            raise ValueError(f"No hay suficiente stock para {producto.n_producto}")
                        
                        # Descontar stock
                        producto.stock -= item['cantidad']
                        producto.save()
                        
                        Producto_Venta.objects.create(
                            id_venta=venta,
                            id_producto=producto,
                            cantidad=item['cantidad'],
                            precio_unitario=item['precio']
                        )
                    
                    # Crear registro de logística
                    Logistica.objects.create(venta=venta)
                    
                    # Incrementar usos del cupón si se usó uno
                    cupon_usado = request.session.get('cupon_usado')
                    if cupon_usado:
                        try:
                            cupon = Cupon.objects.get(codigo=cupon_usado)
                            cupon.usos_actuales += 1
                            cupon.save()
                        except Cupon.DoesNotExist:
                            pass
                    
                    venta_id = venta.id

                    ####PARTE DEL CORREO
                    try:
                        # Obtener el usuario recién creado/actualizado
                        cliente = usuario
                        
                        # Construir lista de productos
                        lista_productos = ""
                        for id_prod, item in carrito.items():
                            lista_productos += f"   • {item['nombre']} x {item['cantidad']} unidades - ${item['subtotal']:,.0f}\n"
                        
                        subject = '✅ ¡Compra confirmada! - KRD Club'
                        message = f'''
¡Hola {cliente.nombre}! 👋

¡Gracias por tu compra en KRD Club! 🎉

Tu pago ha sido procesado exitosamente via WEBPAY.

📋 DETALLE DE TU PEDIDO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
N° de Orden: #{venta_id}
Fecha: {venta.fecha_venta.strftime('%d/%m/%Y %H:%M')}

🛒 PRODUCTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{lista_productos}
💰 TOTAL PAGADO: ${total:,.0f}

📍 DIRECCIÓN DE ENVÍO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{cliente.direccion}

📦 ¿QUÉ SIGUE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Estamos preparando tu pedido
2. Te notificaremos cuando sea despachado
3. Recibirás el número de seguimiento por correo

⏰ Tiempo estimado de entrega: 2 a 5 días hábiles
.

¡Gracias por confiar en nosotros! 🏎️

Saludos,
El equipo de KRD Club ❤️
'''
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [cliente.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Error enviando correo de confirmación: {e}")
                        # No fallar la compra si el correo falla
                    
            except Exception as e:
                # Error al crear la venta - informar al usuario
                messages.error(request, f"Error al procesar la compra: {str(e)}")
                return redirect('ver_carrito')
            
            # Limpiar sesión completamente (incluido el carrito y cupón)
            for key in ['cliente_temp', 'total_venta', 'webpay_token', 'webpay_buy_order', 'carrito', 'cupon_codigo', 'cupon_usado', 'descuento_aplicado']:
                request.session.pop(key, None)
            request.session.modified = True
            
            messages.success(request, f"¡Pago exitoso! Tu número de orden es #{venta_id}")
            return render(request, 'compra_exitosa.html', {
                'venta_id': venta_id,
                'response': response,
            })
        else:
            # Pago rechazado /// NO se crea ninguna venta
            # El carrito se mantiene disponible!!!!!!
            for key in ['cliente_temp', 'total_venta', 'webpay_token', 'webpay_buy_order']:
                request.session.pop(key, None)
            request.session.modified = True
            
            return render(request, 'compra_rechazada.html', {
                'total': total,
                'response': response,
            })
            
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {str(e)}")
        return redirect('ver_carrito')
            
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {str(e)}")
        return redirect('ver_carrito')

### Contador carrito ES X CACHÉ
def contador_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return JsonResponse({"total_items": total_items})


### PANEL DE ADMINISTRACIÓN

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

def admin_dashboard(request):
    """Dashboard principal del panel de administración"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    from django.utils import timezone
    from datetime import timedelta, datetime
    from django.db.models.functions import TruncDate, TruncMonth
    import json
    
    # Usar datetime completos para compatibilidad con SQLite
    ahora = timezone.now()
    hoy = timezone.localtime(ahora).date()
    
    # Crear datetimes aware para los filtros<
    inicio_hoy = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    fin_hoy = inicio_hoy + timedelta(days=1)
    
    inicio_semana = timezone.make_aware(datetime.combine(hoy - timedelta(days=hoy.weekday()), datetime.min.time()))
    
    inicio_mes = timezone.make_aware(datetime.combine(hoy.replace(day=1), datetime.min.time()))
    
    # Estadísticas generales
    total_ventas = Venta.objects.count()
    total_ingresos = Venta.objects.aggregate(total=Sum('precio_venta'))['total'] or 0
    total_productos = Producto.objects.count()
    total_stock = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    
    # Ventas del día
    ventas_hoy = Venta.objects.filter(fecha_venta__gte=inicio_hoy, fecha_venta__lt=fin_hoy).count()
    ingresos_hoy = Venta.objects.filter(fecha_venta__gte=inicio_hoy, fecha_venta__lt=fin_hoy).aggregate(total=Sum('precio_venta'))['total'] or 0
    
    # Ventas de la semana
    ventas_semana = Venta.objects.filter(fecha_venta__gte=inicio_semana).count()
    ingresos_semana = Venta.objects.filter(fecha_venta__gte=inicio_semana).aggregate(total=Sum('precio_venta'))['total'] or 0
    
    # Ventas del mes
    ventas_mes = Venta.objects.filter(fecha_venta__gte=inicio_mes).count()
    ingresos_mes = Venta.objects.filter(fecha_venta__gte=inicio_mes).aggregate(total=Sum('precio_venta'))['total'] or 0
    
    # Envíos pendientes
    envios_pendientes = Logistica.objects.filter(estado='pendiente').count()
    envios_enviados = Logistica.objects.filter(estado='enviado').count()
    
    # Ventas últimos 7 días para gráfico
    ventas_7_dias = []
    labels_7_dias = []
    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=i)
        inicio_dia = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
        fin_dia = inicio_dia + timedelta(days=1)
        total = Venta.objects.filter(fecha_venta__gte=inicio_dia, fecha_venta__lt=fin_dia).aggregate(total=Sum('precio_venta'))['total'] or 0
        ventas_7_dias.append(int(total))
        labels_7_dias.append(fecha.strftime('%d/%m'))
    
    # Ventas últimos 6 meses para gráfico
    ventas_mensuales = []
    labels_mensuales = []
    for i in range(5, -1, -1):
        mes = hoy.month - i
        anio = hoy.year
        if mes <= 0:
            mes += 12
            anio -= 1
        fecha_inicio = timezone.make_aware(datetime(anio, mes, 1))
        if mes == 12:
            fecha_fin = timezone.make_aware(datetime(anio+1, 1, 1))
        else:
            fecha_fin = timezone.make_aware(datetime(anio, mes+1, 1))
        total = Venta.objects.filter(fecha_venta__gte=fecha_inicio, fecha_venta__lt=fecha_fin).aggregate(total=Sum('precio_venta'))['total'] or 0
        ventas_mensuales.append(int(total))
        labels_mensuales.append(fecha_inicio.strftime('%b'))
    
    # Productos más vendidos
    productos_vendidos = Producto_Venta.objects.values('id_producto__n_producto').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    # Umbral de bajo stock (configurable, guardado en BD)
    # Si viene por POST, guardar en BD
    if request.method == 'POST' and 'umbral_stock' in request.POST:
        nuevo_umbral = request.POST.get('umbral_stock', '5')
        try:
            nuevo_umbral = int(nuevo_umbral)
            if nuevo_umbral < 0:
                nuevo_umbral = 0
            if nuevo_umbral > 100:
                nuevo_umbral = 100
            Configuracion.set_valor('umbral_bajo_stock', str(nuevo_umbral), 'Cantidad para considerar bajo stock')
        except ValueError:
            pass
    
    # Obtener umbral desde BD (default: 5)
    umbral_bajo_stock = int(Configuracion.get_valor('umbral_bajo_stock', '5'))
    
    # Productos con bajo stock
    productos_bajo_stock = Producto.objects.filter(stock__lte=umbral_bajo_stock).order_by('stock')[:10]
    
    # Últimas 5 ventas
    ultimas_ventas = Venta.objects.prefetch_related('productos_venta').order_by('-fecha_venta')[:5]
    
    context = {
        # Stats generales
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'total_productos': total_productos,
        'total_stock': total_stock,
        # Stats del día
        'ventas_hoy': ventas_hoy,
        'ingresos_hoy': ingresos_hoy,
        # Stats semana
        'ventas_semana': ventas_semana,
        'ingresos_semana': ingresos_semana,
        # Stats mes
        'ventas_mes': ventas_mes,
        'ingresos_mes': ingresos_mes,
        # Logística
        'envios_pendientes': envios_pendientes,
        'envios_enviados': envios_enviados,
        # Datos para gráficos (JSON)
        'ventas_7_dias': json.dumps(ventas_7_dias),
        'labels_7_dias': json.dumps(labels_7_dias),
        'ventas_mensuales': json.dumps(ventas_mensuales),
        'labels_mensuales': json.dumps(labels_mensuales),
        # Listas
        'productos_vendidos': productos_vendidos,
        'productos_bajo_stock': productos_bajo_stock,
        'umbral_bajo_stock': umbral_bajo_stock,
        'ultimas_ventas': ultimas_ventas,
    }
    
    return render(request, 'panel/dashboard.html', context)


def admin_productos(request):
    """Lista de productos para administración"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    productos = Producto.objects.all().order_by('-id_producto')
    stock_total = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    
    return render(request, 'panel/productos.html', {
        'productos': productos,
        'stock_total': stock_total,
    })


def admin_ventas(request):
    """Lista de ventas para administración"""
    from django.utils import timezone
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    ventas = Venta.objects.prefetch_related('productos_venta__id_producto').order_by('-fecha_venta')
    
    for venta in ventas:
        venta.cantidad_total = sum(item.cantidad for item in venta.productos_venta.all())
    
    return render(request, 'panel/ventas.html', {
        'ventas': ventas,
    })


def admin_compras(request):
    """Lista de compras para administración"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    compras = Compra.objects.prefetch_related('productos_compra__producto').order_by('-fecha')
    
    # El precio unitario se ingresa NETO (sin IVA)
    # subtotalc guarda el total neto (cantidad * precio_neto)
    # El IVA se calcula como 19% del neto
    total_neto = Compra.objects.aggregate(total=Sum('subtotalc'))['total'] or 0
    total_iva = round(total_neto * Decimal('0.19'), 0)
    total_bruto = total_neto + total_iva
    
    # Agregar valores calculados a cada compra
    for compra in compras:
        compra.neto = compra.subtotalc  # El subtotalc ya es neto
        compra.iva = round(compra.subtotalc * Decimal('0.19'), 0)
        compra.bruto = compra.neto + compra.iva
    
    return render(request, 'panel/compras.html', {
        'compras': compras,
        'total_neto': total_neto,
        'total_iva': total_iva,
        'total_bruto': total_bruto,
    })


def admin_logistica(request):
    """Panel de logística - gestión de envíos"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    # Crear registros de logística para ventas que no tengan
    ventas_sin_logistica = Venta.objects.filter(logistica__isnull=True)
    for venta in ventas_sin_logistica:
        Logistica.objects.create(venta=venta, estado='pendiente')
    
    # Filtro por estado
    estado_filtro = request.GET.get('estado', 'todos')
    
    logisticas = Logistica.objects.select_related('venta').prefetch_related(
        'venta__productos_venta__id_producto'
    ).order_by('-venta__fecha_venta')
    
    if estado_filtro != 'todos':
        logisticas = logisticas.filter(estado=estado_filtro)
    
    # Agregar datos del usuario a cada logística
    for log in logisticas:
        if log.venta.id_usuario:
            try:
                log.usuario = Usuario.objects.get(rut=log.venta.id_usuario)
            except Usuario.DoesNotExist:
                log.usuario = None
        else:
            log.usuario = None
    
    # Stats
    stats = {
        'pendientes': Logistica.objects.filter(estado='pendiente').count(),
        'enviados': Logistica.objects.filter(estado='enviado').count(),
        'entregados': Logistica.objects.filter(estado='entregado').count(),
        'total': Logistica.objects.count(),
    }
    
    return render(request, 'panel/logistica.html', {
        'logisticas': logisticas,
        'stats': stats,
        'estado_filtro': estado_filtro,
    })


def marcar_enviado(request, venta_id):
    """Marcar una venta como enviada"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    if request.method == 'POST':
        try:
            logistica = get_object_or_404(Logistica, venta_id=venta_id)
            
            empresa = request.POST.get('empresa_envio', '').strip()
            n_seguimiento = request.POST.get('n_seguimiento', '').strip()
            fecha_envio = request.POST.get('fecha_envio', '')
            
            if not empresa or not n_seguimiento or not fecha_envio:
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('admin_logistica')
            
            logistica.empresa_envio = empresa
            logistica.n_seguimiento = n_seguimiento
            logistica.fecha_envio = fecha_envio
            logistica.estado = 'enviado'
            logistica.save()
            
            messages.success(request, f'Venta #{venta_id} marcada como enviada')

            ### CORREO ELECTRONICOOO!!
            rut_cliente = logistica.venta.id_usuario
            try:
                cliente = Usuario.objects.get(rut=rut_cliente)
                venta = logistica.venta
                subject = '🚚 Tu compra ha sido enviada - KRD CLUB'
                message = f'''
¡Hola {cliente.nombre}!👋 

¡Excelentes noticias! 

Tu compra #{venta.id} ha sido entregada a la empresa de reparto: {empresa}.

🔍Para que veas donde va tu pedido, aquí te dejamos el número de seguimiento: {n_seguimiento}.

Estamos atentos al proceso de entrega para que todo salga bien.👌

¡Gracias por confiar en KRD Club!😎

Saludos,
El equipo logístico de KRD ❤️
'''
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [cliente.email],
                    fail_silently=False,
                )
                messages.success(request, f'Correo de envío enviado a {cliente.email}')
            except Usuario.DoesNotExist:
                print("Cliente no encontrado con RUT:", rut_cliente)


        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('admin_logistica')


def marcar_entregado(request, venta_id):
    """Marcar una venta como entregada"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        logistica = get_object_or_404(Logistica, venta_id=venta_id)
        logistica.estado = 'entregado'
        logistica.save()
        messages.success(request, f'Venta #{venta_id} marcada como entregada')
        rut_cliente = logistica.venta.id_usuario
        try:
            cliente = Usuario.objects.get(rut=rut_cliente)
            venta = logistica.venta
            subject = '📦 Recibiste tu pedido - KRD CLUB'
            message = f'''
¡Hola {cliente.nombre}!👋 

¡Confirmamos que tu pedido #{venta.id} ha sido entregado! 🎉


⭐ ¿QUÉ TE PARECIÓ TU COMPRA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tu opinión es muy importante para nosotros.
¡Nos encantaría saber qué te parecieron tus llantas! 

Puedes dejarnos tu valoración ingresando a nuestra página
con tu número de orden #{venta.id} y tu RUT.

🔧 ¿NECESITAS AYUDA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Si tienes algún problema con tu pedido o necesitas 
asesoría para la instalación, no dudes en contactarnos.

¡Gracias por confiar en KRD Club! 🏎️
Esperamos verte pronto.

Saludos,
El equipo de KRD Club ❤️
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [cliente.email],
                fail_silently=False,
                )
        except Usuario.DoesNotExist:
                print("Cliente no encontrado con RUT:", rut_cliente)

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('admin_logistica')


### Login Panel de Administración
from django.contrib.auth import login, logout, authenticate
import re

def formato_rut(rut):
    """Valida formato y dígito verificador de RUT chileno"""
    # Limpiar el RUT
    rut = rut.replace(".", "").replace("-", "").upper()
    
    if len(rut) < 2:
        return False
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    # Validar que el cuerpo sea numérico
    if not cuerpo.isdigit():
        return False
    
    # Calcular dígito verificador
    suma = 0
    multiplo = 2
    
    for i in reversed(cuerpo):
        suma += int(i) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    return dv == dv_calculado


def panel_login(request):
    """Vista de login para el panel de administración"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        password = request.POST.get('password', '')
        
        # Validar RUT chileno
        if not formato_rut(rut):
            messages.error(request, 'El RUT ingresado no es válido.')
            return render(request, 'panel/login.html', {'rut': rut})
        
        # Formatear RUT (quitar puntos y guiones para buscar)
        rut_limpio = rut.replace(".", "").replace("-", "").upper()
        
        # Buscar usuario
        try:
            usuario = Usuario.objects.get(rut=rut_limpio)
            
            # Verificar si es admin
            if not usuario.admin:
                messages.error(request, 'No tienes permisos para acceder al panel.')
                return render(request, 'panel/login.html', {'rut': rut})
            
            # Verificar contraseña
            if usuario.check_password(password):
                login(request, usuario)
                messages.success(request, f'Bienvenido, {usuario.nombre}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
        
        return render(request, 'panel/login.html', {'rut': rut})
    
    return render(request, 'panel/login.html')


def panel_logout(request):
    """Cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('home')


### SISTEMA DE VALORACIONES

def crear_valoracion(request, venta_id):
    """
    el cliente crea una valoración de su compra.
    Solo puede valorar ventas entregadas y que no hayan sido valoradas.
    """
    # Obtener la venta
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Verificar que la venta tenga logística y esté entregada
    try:
        logistica = venta.logistica
        if logistica.estado != 'entregado':
            messages.warning(request, 'Solo puedes valorar compras que ya han sido entregadas.')
            return redirect('home')
    except Logistica.DoesNotExist:
        messages.warning(request, 'Esta venta aún no tiene información de envío.')
        return redirect('home')
    
    # Verificar si ya existe una valoración
    if hasattr(venta, 'valoracion'):
        messages.info(request, 'Ya has valorado esta compra.')
        return redirect('ver_valoracion', venta_id=venta_id)
    
    # Obtener datos del usuario
    usuario = None
    if venta.id_usuario:
        try:
            usuario = Usuario.objects.get(rut=venta.id_usuario)
        except Usuario.DoesNotExist:
            pass
    
    # Obtener productos de la venta
    productos_venta = Producto_Venta.objects.filter(id_venta=venta).select_related('id_producto')
    
    if request.method == 'POST':
        # Procesar el formulario
        estrellas = int(request.POST.get('estrellas', 5))
        comentario = request.POST.get('comentario', '').strip()
        
        # Validar valores entre 1 y 5
        estrellas = max(1, min(5, estrellas))
        
        # Crear la valoración
        Valoracion.objects.create(
            venta=venta,
            rut_usuario=venta.id_usuario or '',
            estrellas=estrellas,
            comentario=comentario if comentario else None,
        )
        
        messages.success(request, '¡Gracias por tu valoración! Tu opinión nos ayuda a mejorar.')
        return redirect('ver_valoracion', venta_id=venta_id)
    
    return render(request, 'valoraciones/crear_valoracion.html', {
        'venta': venta,
        'usuario': usuario,
        'productos_venta': productos_venta,
    })


def ver_valoracion(request, venta_id):
    """Vista para ver una valoración existente"""
    venta = get_object_or_404(Venta, id=venta_id)
    valoracion = get_object_or_404(Valoracion, venta=venta)
    
    # Obtener datos del usuario
    usuario = None
    if venta.id_usuario:
        try:
            usuario = Usuario.objects.get(rut=venta.id_usuario)
        except Usuario.DoesNotExist:
            pass
    
    # Obtener productos de la venta
    productos_venta = Producto_Venta.objects.filter(id_venta=venta).select_related('id_producto')
    
    return render(request, 'valoraciones/ver_valoracion.html', {
        'venta': venta,
        'valoracion': valoracion,
        'usuario': usuario,
        'productos_venta': productos_venta,
    })


def valoraciones_publicas(request):
    """
    Página pública con todas las valoraciones visibles.
    Muestra testimonios de clientes satisfechos.
    """
    valoraciones = Valoracion.objects.select_related('venta').order_by('-fecha_valoracion')[:20]
    
    # Agregar nombre de usuario a cada valoración
    for val in valoraciones:
        try:
            usuario = Usuario.objects.get(rut=val.rut_usuario)
            val.nombre_cliente = f"{usuario.nombre} {usuario.apellido[0]}."
        except Usuario.DoesNotExist:
            val.nombre_cliente = "Cliente"
    
    # Calcular estadísticas
    total_valoraciones = Valoracion.objects.count()
    if total_valoraciones > 0:
        from django.db.models import Avg
        stats = Valoracion.objects.aggregate(
            promedio=Avg('estrellas'),
        )
    else:
        stats = {
            'promedio': 0,
        }
    
    # Distribución por estrellas con porcentajes calculados
    distribucion = []
    for i in range(5, 0, -1):
        count = Valoracion.objects.filter(estrellas=i).count()
        porcentaje = (count / total_valoraciones * 100) if total_valoraciones > 0 else 0
        distribucion.append({
            'estrellas': i,
            'count': count,
            'porcentaje': round(porcentaje, 1)
        })
    
    return render(request, 'valoraciones/valoraciones_publicas.html', {
        'valoraciones': valoraciones,
        'total_valoraciones': total_valoraciones,
        'stats': stats,
        'distribucion': distribucion,
    })


def buscar_venta_valorar(request):
    """
    API para buscar una venta por número de orden y RUT para valorar.
    """
    venta_id = request.GET.get('venta_id', '').strip()
    rut = request.GET.get('rut', '').strip().replace(".", "").replace("-", "").upper()
    
    if not venta_id or not rut:
        return JsonResponse({'success': False, 'message': 'Ingresa el número de orden y tu RUT.'})
    
    try:
        venta = Venta.objects.get(id=venta_id)
        
        # Verificar que el RUT coincida
        rut_venta = venta.id_usuario.replace(".", "").replace("-", "").upper() if venta.id_usuario else ""
        if rut_venta != rut:
            return JsonResponse({'success': False, 'message': 'El RUT no coincide con esta orden.'})
        
        # Verificar si está entregada
        try:
            logistica = venta.logistica
            if logistica.estado != 'entregado':
                return JsonResponse({'success': False, 'message': 'Esta compra aún no ha sido entregada.'})
        except Logistica.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Esta compra aún no tiene información de envío.'})
        
        # Verificar si ya fue valorada
        if hasattr(venta, 'valoracion'):
            return JsonResponse({
                'success': True, 
                'ya_valorada': True,
                'redirect_url': reverse('ver_valoracion', args=[venta_id])
            })
        
        return JsonResponse({
            'success': True,
            'ya_valorada': False,
            'redirect_url': reverse('crear_valoracion', args=[venta_id])
        })
        
    except Venta.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No se encontró una orden con ese número.'})


def admin_anuncios(request):
    """Gestión de anuncios del banner superior"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    # Obtener anuncios actuales
    anuncios_json = Configuracion.get_valor('anuncios', '[]')
    try:
        anuncios = json.loads(anuncios_json)
    except json.JSONDecodeError:
        anuncios = []
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'agregar':
            nuevo_anuncio = {
                'texto': request.POST.get('texto', ''),
                'link': request.POST.get('link', ''),
                'link_texto': request.POST.get('link_texto', 'Ver más'),
                'activo': True
            }
            if nuevo_anuncio['texto']:
                anuncios.append(nuevo_anuncio)
                Configuracion.set_valor('anuncios', json.dumps(anuncios), 'Anuncios del banner superior')
                messages.success(request, 'Anuncio agregado correctamente')
        
        elif action == 'eliminar':
            index = int(request.POST.get('index', -1))
            if 0 <= index < len(anuncios):
                anuncios.pop(index)
                Configuracion.set_valor('anuncios', json.dumps(anuncios), 'Anuncios del banner superior')
                messages.success(request, 'Anuncio eliminado')
        
        elif action == 'toggle':
            index = int(request.POST.get('index', -1))
            if 0 <= index < len(anuncios):
                anuncios[index]['activo'] = not anuncios[index].get('activo', True)
                Configuracion.set_valor('anuncios', json.dumps(anuncios), 'Anuncios del banner superior')
                estado = 'activado' if anuncios[index]['activo'] else 'desactivado'
                messages.success(request, f'Anuncio {estado}')
        
        elif action == 'editar':
            index = int(request.POST.get('index', -1))
            if 0 <= index < len(anuncios):
                anuncios[index]['texto'] = request.POST.get('texto', '')
                anuncios[index]['link'] = request.POST.get('link', '')
                anuncios[index]['link_texto'] = request.POST.get('link_texto', 'Ver más')
                Configuracion.set_valor('anuncios', json.dumps(anuncios), 'Anuncios del banner superior')
                messages.success(request, 'Anuncio actualizado')
        
        return redirect('admin_anuncios')
    
    return render(request, 'panel/anuncios.html', {'anuncios': anuncios})


def admin_cupones(request):
    """Gestión de cupones de descuento"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear':
            codigo = request.POST.get('codigo', '').upper().strip()
            if codigo and not Cupon.objects.filter(codigo=codigo).exists():
                Cupon.objects.create(
                    codigo=codigo,
                    descripcion=request.POST.get('descripcion', ''),
                    tipo=request.POST.get('tipo', 'porcentaje'),
                    valor=int(request.POST.get('valor', 10)),
                    monto_minimo=int(request.POST.get('monto_minimo', 0) or 0),
                    uso_maximo=int(request.POST.get('uso_maximo', 0) or 0),
                    fecha_inicio=request.POST.get('fecha_inicio') or None,
                    fecha_fin=request.POST.get('fecha_fin') or None,
                    activo=True
                )
                messages.success(request, f'Cupón {codigo} creado correctamente')
            else:
                messages.error(request, 'El código ya existe o es inválido')
        
        elif action == 'toggle':
            codigo = request.POST.get('codigo')
            cupon = Cupon.objects.filter(codigo=codigo).first()
            if cupon:
                cupon.activo = not cupon.activo
                cupon.save()
                estado = 'activado' if cupon.activo else 'desactivado'
                messages.success(request, f'Cupón {estado}')
        
        elif action == 'eliminar':
            codigo = request.POST.get('codigo')
            Cupon.objects.filter(codigo=codigo).delete()
            messages.success(request, 'Cupón eliminado')
        
        return redirect('admin_cupones')
    
    cupones = Cupon.objects.all()
    return render(request, 'panel/cupones.html', {'cupones': cupones})


def admin_destacados(request):
    """Gestión de productos destacados"""
    if not request.user.is_authenticated or not getattr(request.user, 'admin', False):
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_login')
    
    # Obtener productos destacados actuales
    productos_destacados = Configuracion.get_productos_destacados()
    productos_destacados_ids = [str(p.id_producto) for p in productos_destacados]
    
    # Obtener todos los productos disponibles (con stock)
    todos_productos = Producto.objects.filter(stock__gt=0).order_by('n_producto')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'agregar':
            producto_id = request.POST.get('producto_id')
            orden = int(request.POST.get('orden', 0))
            if producto_id:
                Configuracion.agregar_producto_destacado(producto_id, orden)
                messages.success(request, 'Producto agregado a destacados')
        
        elif action == 'eliminar':
            producto_id = request.POST.get('producto_id')
            if producto_id:
                Configuracion.eliminar_producto_destacado(producto_id)
                messages.success(request, 'Producto eliminado de destacados')
        
        elif action == 'actualizar_orden':
            producto_id = request.POST.get('producto_id')
            nuevo_orden = int(request.POST.get('orden', 0))
            if producto_id:
                Configuracion.agregar_producto_destacado(producto_id, nuevo_orden)
                messages.success(request, 'Orden actualizado')
        
        elif action == 'guardar_todos':
            # Guardar orden de todos los productos destacados
            nuevos_destacados = []
            for key, value in request.POST.items():
                if key.startswith('orden_'):
                    producto_id = key.replace('orden_', '')
                    orden = int(value) if value else 0
                    nuevos_destacados.append({'id': producto_id, 'orden': orden})
            
            if nuevos_destacados:
                Configuracion.set_productos_destacados(nuevos_destacados)
                messages.success(request, 'Orden de productos actualizado')
        
        return redirect('admin_destacados')
    
    # Obtener info completa de destacados con orden
    destacados_json = Configuracion.get_valor('productos_destacados', '[]')
    try:
        destacados_config = json.loads(destacados_json)
        destacados_dict = {d['id']: d.get('orden', 0) for d in destacados_config}
    except json.JSONDecodeError:
        destacados_dict = {}
    
    # Combinar productos con su orden
    productos_destacados_con_orden = []
    for producto in productos_destacados:
        productos_destacados_con_orden.append({
            'producto': producto,
            'orden': destacados_dict.get(str(producto.id_producto), 0)
        })
    
    return render(request, 'panel/destacados.html', {
        'productos_destacados': productos_destacados_con_orden,
        'productos_destacados_ids': productos_destacados_ids,
        'todos_productos': todos_productos,
    })

