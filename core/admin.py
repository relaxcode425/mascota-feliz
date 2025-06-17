from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Reserva, Dueno, Mascota, ServicioDomicilio, FichaMedica, Entrada

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Tipo de usuario', {'fields': ('tipo_usuario',)}),
    )
    list_display = ['username', 'email', 'tipo_usuario', 'is_staff']

admin.site.register(Usuario, UsuarioAdmin)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_servicio', 'tipo_reserva', 'fecha', 'hora', 'fecha_creacion', 'estado']
    list_filter = ['tipo_servicio', 'tipo_reserva', 'fecha', 'estado']
    search_fields = ['cliente__username']

@admin.register(Dueno)
class DuenoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'usuario', 'contacto', 'direccion']
    search_fields = ['nombre', 'rut', 'usuario__username']

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'raza', 'color', 'dueno']
    search_fields = ['nombre', 'raza', 'dueno__nombre']

@admin.register(ServicioDomicilio)
class ServicioDomicilioAdmin(admin.ModelAdmin):
    list_display = [
        'reserva',
        'num_estilistas',
        'num_veterinarios',
        'tipo_equipo',
        'horario_asignado',
        'estado',
    ]
    search_fields = ['reserva__id', 'reserva__cliente__username', 'estado']
    list_filter = ['estado']

@admin.register(FichaMedica)
class FichaMedicaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'edad', 'peso']
    search_fields = ['mascota__nombre']

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ['ficha_medica', 'fecha', 'descripcion']
    search_fields = ['ficha_medica__mascota__nombre', 'descripcion']