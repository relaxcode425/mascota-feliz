from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Usuario(AbstractUser):
    TIPOS = [
        ('operador', 'Operador de agenda'),
        ('cliente', 'Cliente'),
        ('recepcion', 'Recepción'),
        ('veterinario', 'Veterinario'),
        ('estilista', 'Estilista'),
        ('ventas', 'Vendedor'),
    ]
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS, default='cliente')

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"


class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('en_camino', 'En camino'),         # solo a domicilio
        ('en_espera', 'En espera'),         # solo presencial
        ('en_atencion', 'En atención'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No asistió'),
    ]
    TIPO_SERVICIO_CHOICES = [
        ('veterinario', 'Veterinario'),
        ('estetico', 'Estético'),
    ]
    TIPO_RESERVA_CHOICES = [
        ('presencial', 'Presencial'),
        ('domicilio', 'A domicilio'),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'cliente'})
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES)
    tipo_reserva = models.CharField(max_length=20, choices=TIPO_RESERVA_CHOICES)
    direccion = models.CharField(max_length=255, blank=True, null=True)  # obligatoria si es a domicilio
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha = models.DateField()
    hora = models.TimeField()

    def __str__(self):
        return f"{self.cliente.username} - {self.tipo_servicio} - {self.fecha} {self.hora}"


User = get_user_model()

class Dueno(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'cliente'})
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Mascota(models.Model):
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
    ]
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    chip = models.CharField(max_length=30, blank=True, null=True)
    raza = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, default='macho')

    def __str__(self):
        return f"{self.nombre} ({self.raza})"

class ServicioDomicilio(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, limit_choices_to={'tipo_reserva': 'domicilio'})
    equipo = models.CharField(max_length=255)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Domicilio - {self.reserva}"
    
class FichaMedica(models.Model):
    mascota = models.OneToOneField(Mascota, on_delete=models.CASCADE)
    edad = models.IntegerField()
    peso = models.FloatField()

    def __str__(self):
        return f"Ficha {self.mascota.nombre}"

class Entrada(models.Model):
    ficha_medica = models.ForeignKey(FichaMedica, on_delete=models.CASCADE, related_name='entradas')
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Entrada - {self.ficha_medica.mascota.nombre} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
