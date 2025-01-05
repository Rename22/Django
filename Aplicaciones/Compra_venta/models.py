from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)  # Cédula única
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)  # Correo único
    contrasena = models.CharField(max_length=128)  # Contraseña encriptada


class Libro(models.Model):
    CONDICIONES = [
        ('Nuevo', 'Nuevo'),
        ('Usado', 'Usado'),
    ]

    CATEGORIAS = [
        ('Ficción', 'Ficción'),
        ('No Ficción', 'No Ficción'),
        ('Fantasía', 'Fantasía'),
        ('Ciencia Ficción', 'Ciencia Ficción'),
        ('Romance', 'Romance'),
        ('Misterio', 'Misterio'),
        ('Historia', 'Historia'),
        ('Biografía', 'Biografía'),
        ('Infantil', 'Infantil'),
        ('Autoayuda', 'Autoayuda'),
        ('Otros', 'Otros'),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='libros/', blank=True, null=True)
    condicion = models.CharField(max_length=50, choices=CONDICIONES)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Otros')
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='libros_vendidos')
    vendido = models.BooleanField(default=False)  # Indica si el libro fue vendido
    en_proceso = models.BooleanField(default=False)  # Nuevo campo para indicar si está en proceso
    creado_en = models.DateTimeField(auto_now_add=True)



class Orden(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),    # El comprador envió la solicitud
        ('Aceptada', 'Aceptada'),     # El vendedor aceptó la solicitud
        ('Rechazada', 'Rechazada'),   # El vendedor rechazó la solicitud
        ('Completada', 'Completada'), # El vendedor confirmó la entrega
    ]

    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ordenes_compradas')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ordenes')
    lugar_encuentro = models.CharField(max_length=255)
    fecha_encuentro = models.DateField()
    hora_encuentro = models.TimeField()
    estado = models.CharField(max_length=50, choices=ESTADOS, default='Pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True, null=True)



class Notificacion(models.Model):
    TIPOS = [
        ('Nueva solicitud', 'Nueva solicitud'),
        ('Aceptada', 'Aceptada'),
        ('Rechazada', 'Rechazada'),
        ('Completada', 'Completada'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPOS)
    leida = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
