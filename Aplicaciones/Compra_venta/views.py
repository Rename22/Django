from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistroUsuarioForm
from .models import Libro, Orden, Usuario, Notificacion



def inicio(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')  # Redirige si no está autenticado

    usuario_id = request.session['usuario_id']
    usuario = Usuario.objects.get(id=usuario_id)

    # Obtener los filtros de la solicitud GET
    categoria = request.GET.get('categoria', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    busqueda = request.GET.get('busqueda', '')

    # Filtrar libros disponibles (no vendidos y no en proceso)
    libros = Libro.objects.filter(vendido=False, en_proceso=False).exclude(vendedor_id=usuario_id)

    # Aplicar filtros sin usar Q
    if categoria:
        libros = libros.filter(categoria=categoria)
    if precio_min:
        libros = libros.filter(precio__gte=precio_min)
    if precio_max:
        libros = libros.filter(precio__lte=precio_max)
    if busqueda:
        # Filtrar por título
        libros_titulo = libros.filter(titulo__icontains=busqueda)
        # Filtrar por autor
        libros_autor = libros.filter(autor__icontains=busqueda)
        # Unir los resultados (remueve duplicados si existen)
        libros = libros_titulo | libros_autor

    return render(request, 'inicio.html', {'libros': libros, 'usuario': usuario})


def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        try:
            usuario = Usuario.objects.get(correo=correo)
            if usuario.contrasena == contrasena: 
                request.session['usuario_id'] = usuario.id  
                messages.success(request, f"Bienvenido, {usuario.nombre}")
                return redirect('inicio')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "El correo no está registrado.")

    return render(request, 'login.html')

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('login')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registrar.html', {'form': form})

def cerrar_sesion(request):
    if 'usuario_id' in request.session:
        del request.session['usuario_id']  
    return redirect('login')


# GESTIONAR LIBROS 
def productos(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')
    
    usuario_id = request.session['usuario_id']
    libros = Libro.objects.filter(vendedor_id=usuario_id)
    return render(request, 'productos.html', {'libros': libros})

def agregar_libro(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')

    if request.method == 'POST':
        titulo = request.POST['titulo']
        autor = request.POST['autor']
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST['precio']
        condicion = request.POST['condicion']
        categoria = request.POST['categoria']
        imagen = request.FILES.get('imagen')

        usuario_id = request.session['usuario_id']
        Libro.objects.create(
            titulo=titulo,
            autor=autor,
            descripcion=descripcion,
            precio=precio,
            condicion=condicion,
            categoria=categoria,
            imagen=imagen,
            vendedor_id=usuario_id
        )
        return redirect('/productos/')

    return render(request, 'agregar_libro.html', {
        'condiciones': Libro.CONDICIONES,
        'categorias': Libro.CATEGORIAS,
    })

def editar_libro(request, libro_id):
    if 'usuario_id' not in request.session:
        return redirect('/login/')  # Redirige si no está autenticado

    vendedor_id = request.session['usuario_id']

    try:
        libro = Libro.objects.get(id=libro_id, vendedor_id=vendedor_id)

        # Bloquear si el libro está en proceso de compra
        if libro.en_proceso:
            messages.error(request, 'No puedes editar un libro que está en proceso de compra.')
            return redirect('/productos/')

        if request.method == 'POST':
            libro.titulo = request.POST.get('titulo')
            libro.precio = request.POST.get('precio')
            # Actualiza otros campos según sea necesario
            libro.save()
            messages.success(request, 'El libro ha sido actualizado.')
            return redirect('/productos/')

        return render(request, 'editar_libro.html', {'libro': libro})
    except Libro.DoesNotExist:
        messages.error(request, 'El libro no existe o no tienes permisos.')
        return redirect('/productos/')



def eliminar_libro(request, libro_id):
    if 'usuario_id' not in request.session:
        return redirect('/login/')  # Redirige si no está autenticado

    vendedor_id = request.session['usuario_id']

    try:
        libro = Libro.objects.get(id=libro_id, vendedor_id=vendedor_id)

        # Bloquear si el libro está en proceso de compra
        if libro.en_proceso:
            messages.error(request, 'No puedes eliminar un libro que está en proceso de compra.')
            return redirect('/productos/')

        libro.delete()
        messages.success(request, 'El libro ha sido eliminado.')
        return redirect('/productos/')
    except Libro.DoesNotExist:
        messages.error(request, 'El libro no existe o no tienes permisos.')
        return redirect('/productos/')


def comprar_libro(request, libro_id):
    if 'usuario_id' not in request.session:
        return redirect('login')  # Redirige si no está autenticado

    comprador_id = request.session['usuario_id']
    comprador = Usuario.objects.get(id=comprador_id)

    try:
        # Validar que el libro esté disponible y no esté en proceso
        libro = Libro.objects.get(id=libro_id, vendido=False, en_proceso=False)
    except Libro.DoesNotExist:
        messages.error(request, "El libro no está disponible.")
        return redirect('inicio')

    if request.method == 'POST':
        lugar_encuentro = request.POST.get('lugar_encuentro')
        fecha_encuentro = request.POST.get('fecha_encuentro')
        hora_encuentro = request.POST.get('hora_encuentro')

        # Crear la orden
        orden = Orden.objects.create(
            comprador=comprador,
            libro=libro,
            lugar_encuentro=lugar_encuentro,
            fecha_encuentro=fecha_encuentro,
            hora_encuentro=hora_encuentro
        )

        # Marcar el libro como en proceso
        libro.en_proceso = True
        libro.save()

        # Crear una notificación para el vendedor
        mensaje = f"Tienes una nueva solicitud de compra para el libro '{libro.titulo}'."
        Notificacion.objects.create(usuario=libro.vendedor, mensaje=mensaje, tipo='Nueva solicitud')

        messages.success(request, '¡Tu solicitud ha sido enviada al vendedor!')
        return redirect('inicio')

    return render(request, 'comprar_libro.html', {'libro': libro})



def gestionar_solicitudes(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')  # Redirige si no está autenticado

    vendedor_id = request.session['usuario_id']

    ordenes_pendientes = Orden.objects.filter(libro__vendedor_id=vendedor_id, estado='Pendiente')
    ordenes_aceptadas = Orden.objects.filter(libro__vendedor_id=vendedor_id, estado='Aceptada')

    if request.method == 'POST':
        orden_id = request.POST.get('orden_id')
        accion = request.POST.get('accion')  # 'aceptar', 'rechazar', 'cancelar'
        motivo = request.POST.get('motivo', '')  # El motivo es opcional y solo relevante para ciertas acciones

        try:
            orden = Orden.objects.get(id=orden_id, libro__vendedor_id=vendedor_id)
            if accion == 'aceptar':
                orden.estado = 'Aceptada'
                orden.libro.en_proceso = True  # El libro sigue en proceso
                orden.libro.save()
                orden.save()
                messages.success(request, f"La solicitud para el libro '{orden.libro.titulo}' ha sido aceptada.")
            elif accion == 'rechazar':
                orden.estado = 'Rechazada'
                orden.motivo = motivo  # Guarda el motivo
                orden.libro.en_proceso = False  # El libro vuelve a estar disponible
                orden.libro.save()
                orden.save()
                messages.warning(request, f"La solicitud para el libro '{orden.libro.titulo}' ha sido rechazada.")
            elif accion == 'cancelar':
                orden.estado = 'Cancelada'
                orden.motivo = motivo  # Guarda el motivo
                orden.libro.en_proceso = False  # El libro vuelve a estar disponible
                orden.libro.save()
                orden.save()
                messages.info(request, f"La venta del libro '{orden.libro.titulo}' ha sido cancelada.")
        except Orden.DoesNotExist:
            messages.error(request, 'La solicitud no existe o no tienes permisos.')

        return redirect('/solicitudes/')

    return render(request, 'gestionar_solicitudes.html', {
        'ordenes_pendientes': ordenes_pendientes,
        'ordenes_aceptadas': ordenes_aceptadas,
    })

def completar_orden(request, orden_id):
    if 'usuario_id' not in request.session:
        return redirect('login')  # Redirige si no está autenticado

    vendedor_id = request.session['usuario_id']

    try:
        orden = Orden.objects.get(id=orden_id, libro__vendedor_id=vendedor_id, estado='Aceptada')

        # Marcar la orden como completada y el libro como vendido
        orden.estado = 'Completada'
        orden.libro.vendido = True
        orden.libro.en_proceso = False
        orden.libro.save()
        orden.save()

        # Crear notificación para el comprador
        mensaje = f"La compra del libro '{orden.libro.titulo}' ha sido confirmada por el vendedor."
        Notificacion.objects.create(usuario=orden.comprador, mensaje=mensaje, tipo='Completada')

        messages.success(request, f"El libro '{orden.libro.titulo}' ha sido marcado como vendido.")
    except Orden.DoesNotExist:
        messages.error(request, 'La orden no existe o no tienes permisos.')

    return redirect('/solicitudes/')


def mis_solicitudes(request):
    if 'usuario_id' not in request.session:
        return redirect('login')  # Redirige si no está autenticado

    comprador_id = request.session['usuario_id']

    # Obtener todas las órdenes del comprador actual
    solicitudes = Orden.objects.filter(comprador_id=comprador_id).select_related('libro')

    return render(request, 'mis_solicitudes.html', {'solicitudes': solicitudes})

    
def reporte_ventas(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')  # Redirige si no está autenticado

    vendedor_id = request.session['usuario_id']
    # Filtrar ventas completadas
    ventas = Orden.objects.filter(libro__vendedor_id=vendedor_id, estado='Completada')

    return render(request, 'reporte_ventas.html', {'ventas': ventas})