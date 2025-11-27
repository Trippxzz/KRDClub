from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, ProductoImagen, Compra, ProductoCompra, vehiculo, Producto_Vehiculo, Venta, Producto_Venta, Usuario
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
    return render(request, "public/home.html", {'marcas': marcas})


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
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    cilindrada = request.GET.get('cilindrada', '')
    anio = request.GET.get('anio', '')
    
    # Buscar el vehículo
    vehiculos_encontrados = vehiculo.objects.filter(
        marca=marca,
        modelo=modelo,
        cilindrada=cilindrada,
        anio=anio
    )
    
    if vehiculos_encontrados.exists():
        # Obtener productos compatibles
        productos_ids = Producto_Vehiculo.objects.filter(
            vehiculo__in=vehiculos_encontrados
        ).values_list('producto_id', flat=True)
        
        return JsonResponse({
            'success': True,
            'redirect_url': f'/catalogo/?vehiculo_ids={",".join(str(p) for p in productos_ids)}'
        })
    
    return JsonResponse({'success': False, 'message': 'No se encontraron productos para este vehículo'})

def sobre_nosotros(request):
    """
    Página 'Sobre nosotros'
    """
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

            return redirect("listar_compras")
    else:
        form = CompraForm()

    return render(request, "compras/crear.html", {
        "form": form,
        "productos": Producto.objects.all()
    })

def listar_compras(request):
    compras = Compra.objects.all()
    return render(request, "compras/lista.html", {"compras": compras})

def agregar_vehiculos(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vehiculo')
    else:
        form = VehiculoForm()
    return render(request, 'vehiculos/agregar.html', {'form': form})

def lista_vehiculo(request):
    vehiculos = vehiculo.objects.all()
    return render(request, 'vehiculos/lista.html', {'vehiculos': vehiculos})

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
        # Verificar si hay filtro por vehículo
        vehiculo_ids = request.GET.get('vehiculo_ids', '')
        
        if vehiculo_ids:
            # Filtrar productos por IDs de productos compatibles con vehículos
            producto_ids = vehiculo_ids.split(',')
            prods = Producto.objects.filter(id_producto__in=producto_ids)
        else:
            prods = Producto.objects.all()
            
        return render(request, "productos/catalogo.html", {"prods": prods, "filtrado_vehiculo": bool(vehiculo_ids)})
    

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
    total = sum(item['subtotal'] for item in carrito.values())
    return render(request, 'carrito/carrito.html', {'carrito': carrito, 'total': total})

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



### SECCION CONTROL DE STOCK Y SEGURIDAD
@transaction.atomic
def procesarCompra(request):
    """Muestra el formulario de checkout con datos del usuario"""
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect("ver_carrito")
    
    # Validar que todas las cantidades sean múltiplos de 4
    for id_producto, item in carrito.items():
        if item['cantidad'] % 4 != 0:
            messages.error(request, f"La cantidad de {item['nombre']} debe ser múltiplo de 4.")
            return redirect("ver_carrito")
    
    total = sum(item['subtotal'] for item in carrito.values())
    
    if request.method == 'POST':
        # Procesar el formulario y crear la venta
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
                'total': total,
                'datos': request.POST
            })
        
        try:
            with transaction.atomic():
                # Crear o actualizar usuario
                usuario, created = Usuario.objects.update_or_create(
                    rut=rut,
                    defaults={
                        'nombre': nombre,
                        'apellido': apellido,
                        'email': email,
                        'telefono': int(telefono),
                        'direccion': direccion,
                    }
                )
                
                # Crear la venta
                venta = Venta.objects.create(
                    id_usuario=rut,
                    precio_venta=total,
                )
                
                # Crear productos de la venta (sin descontar stock aún)
                for id_producto, item in carrito.items():
                    producto = Producto.objects.select_for_update().get(id_producto=id_producto)
                    
                    if producto.stock < item['cantidad']:
                        raise ValueError(f"No hay suficiente stock para {producto.n_producto}")
                    
                    # NO descontar stock aquí - se descuenta al confirmar el pago
                    
                    Producto_Venta.objects.create(
                        id_venta=venta,
                        id_producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio']
                    )
                
                # Guardar ID de venta en sesión para Webpay
                request.session['venta_pendiente'] = venta.id
                request.session['total_venta'] = int(total)
                
                # Vaciar carrito
                request.session['carrito'] = {}
                request.session.modified = True
                
                # TODO: Redirigir a Webpay
                # Por ahora redirigir a página de éxito
                messages.success(request, f"Venta #{venta.id} creada. Redirigiendo a Webpay...")
                return redirect('webpay_iniciar')
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('ver_carrito')
        except Exception as e:
            messages.error(request, f"Error al procesar la compra: {str(e)}")
            return redirect('ver_carrito')
    
    return render(request, 'checkout.html', {
        'carrito': carrito,
        'total': total,
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
    venta_id = request.session.get('venta_pendiente')
    total = request.session.get('total_venta')
    
    if not venta_id or not total:
        messages.error(request, "No hay una venta pendiente de pago.")
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
        
        # Generar buy_order y session_id únicos
        buy_order = f"orden_{venta_id}_{int(time.time())}"
        session_id = f"sesion_{venta_id}_{int(time.time())}"
        amount = int(total)  # Webpay requiere enteros
        
        # URLs de retorno
        return_url = request.build_absolute_uri(reverse('webpay_retorno'))
        
        # Crear transacción - devuelve un diccionario
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
        # Si falla, mostrar página de simulación como fallback
        return render(request, 'webpay.html', {
            'venta_id': venta_id,
            'total': total,
            'error': str(e),
        })


def webpay_retorno(request):
    """Procesa el retorno de Webpay Plus"""
    # Obtener token de la respuesta (puede venir por GET o POST)
    token = request.GET.get('token_ws') or request.POST.get('token_ws')
    
    # Si el usuario canceló el pago
    if request.GET.get('TBK_TOKEN') or not token:
        venta_id = request.session.get('venta_pendiente')
        if venta_id:
            # Eliminar la venta pendiente (el stock no fue descontado)
            try:
                venta = Venta.objects.get(id=venta_id)
                venta.delete()
            except Venta.DoesNotExist:
                pass
            
            # Limpiar sesión
            for key in ['venta_pendiente', 'total_venta', 'webpay_token', 'webpay_buy_order']:
                request.session.pop(key, None)
            request.session.modified = True
        
        messages.warning(request, "El pago fue cancelado.")
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
        
        venta_id = request.session.get('venta_pendiente')
        
        # Verificar que el pago fue exitoso
        # response es un diccionario con keys: vci, amount, status, buy_order, session_id, etc.
        if response.get('status') == 'AUTHORIZED' and response.get('response_code') == 0:
            # Pago exitoso - AHORA descontar el stock
            try:
                venta = Venta.objects.get(id=venta_id)
                with transaction.atomic():
                    for pv in venta.productos_venta.all():
                        producto = Producto.objects.select_for_update().get(id_producto=pv.id_producto.id_producto)
                        producto.stock -= pv.cantidad
                        producto.save()
            except Venta.DoesNotExist:
                pass
            
            # Limpiar sesión
            for key in ['venta_pendiente', 'total_venta', 'webpay_token', 'webpay_buy_order']:
                request.session.pop(key, None)
            request.session.modified = True
            
            messages.success(request, f"¡Pago exitoso! Tu número de orden es #{venta_id}")
            return render(request, 'compra_exitosa.html', {
                'venta_id': venta_id,
                'response': response,
            })
        else:
            # Pago rechazado - eliminar venta pendiente (stock no fue descontado)
            total = request.session.get('total_venta')
            if venta_id:
                try:
                    venta = Venta.objects.get(id=venta_id)
                    venta.delete()
                except Venta.DoesNotExist:
                    pass
            
            for key in ['venta_pendiente', 'total_venta', 'webpay_token', 'webpay_buy_order']:
                request.session.pop(key, None)
            request.session.modified = True
            
            return render(request, 'compra_rechazada.html', {
                'venta_id': venta_id,
                'total': total,
                'response': response,
            })
            
    except Exception as e:
        messages.error(request, f"Error al procesar el pago: {str(e)}")
        return redirect('ver_carrito')

### Contador carrito
def contador_carrito(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return JsonResponse({"total_items": total_items})


### ==================== PANEL DE ADMINISTRACIÓN ====================

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

def admin_dashboard(request):
    """Dashboard principal del panel de administración"""
    
    return render(request, 'admin/dashboard.html')


def admin_productos(request):
    """Lista de productos para administración"""
    productos = Producto.objects.all().order_by('-id_producto')
    stock_total = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    
    return render(request, 'admin/productos.html', {
        'productos': productos,
        'stock_total': stock_total,
    })


def admin_ventas(request):
    """Lista de ventas para administración"""
    from django.utils import timezone
    
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Filtros de fecha
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    ventas = Venta.objects.prefetch_related('productos_venta__id_producto').order_by('-fecha_venta')
    
    if fecha_desde:
        ventas = ventas.filter(fecha_venta__date__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha_venta__date__lte=fecha_hasta)
    
    # Agregar cantidad total a cada venta
    for venta in ventas:
        venta.cantidad_total = sum(item.cantidad for item in venta.productos_venta.all())
    
    # Stats
    stats = {
        'ventas_hoy': Venta.objects.filter(
            fecha_venta__date=hoy
        ).aggregate(total=Sum('precio_venta'))['total'] or 0,
        'ventas_semana': Venta.objects.filter(
            fecha_venta__date__gte=inicio_semana
        ).aggregate(total=Sum('precio_venta'))['total'] or 0,
        'ventas_mes': Venta.objects.filter(
            fecha_venta__date__gte=inicio_mes
        ).aggregate(total=Sum('precio_venta'))['total'] or 0,
        'total_ventas': ventas.count(),
    }
    
    return render(request, 'admin/ventas.html', {
        'ventas': ventas,
        'stats': stats,
    })


def admin_compras(request):
    """Lista de compras para administración"""
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
    
    return render(request, 'admin/compras.html', {
        'compras': compras,
        'total_neto': total_neto,
        'total_iva': total_iva,
        'total_bruto': total_bruto,
    })