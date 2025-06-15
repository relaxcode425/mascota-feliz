from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Tipo de usuario', {'fields': ('tipo_usuario',)}),
    )
    list_display = ['username', 'email', 'tipo_usuario', 'is_staff']

admin.site.register(Usuario, UsuarioAdmin)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_servicio', 'tipo_reserva', 'fecha', 'hora', 'creada_en']
    list_filter = ['tipo_servicio', 'tipo_reserva', 'fecha']
    search_fields = ['cliente__username']