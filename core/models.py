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

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES)
    tipo_reserva = models.CharField(max_length=20, choices=TIPO_RESERVA_CHOICES)
    fecha = models.DateField()
    hora = models.TimeField()
    creada_en = models.DateTimeField(auto_now_add=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"{self.cliente.username} - {self.tipo_servicio} - {self.fecha} {self.hora}"
