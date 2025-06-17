from django.urls import path, include
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    # Flexibles
    path('panel/', views.panel_principal, name='panel'),
    path('reservas/', views.ver_reservas_cliente, name='ver_reservas'),
    path('mascota/<int:mascota_id>/', views.ver_mascota, name='ver_mascota'),
    path('dueno/', views.ver_dueno, name='ver_dueno'),
    #Funcionalidades cliente
    path('reservar/', views.reservar_servicio, name='reservar_servicio'),
    path('reservar/fecha/', views.seleccionar_fecha, name='seleccionar_fecha'),
    path('reservar/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservar/exito/', TemplateView.as_view(template_name='pages/cliente/reserva_exitosa.html'), name='reserva_exitosa'),
    path('cliente/reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva_cliente, name='cancelar_reserva_cliente'),
    path('cliente/mascotas/', views.ver_mis_mascotas, name='ver_mis_mascotas'),
    # Funcionalidades recepcion
    path('reserva/<int:reserva_id>/cambiar_estado/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado_reserva'),
    path('recepcion/registrar-dueno/', views.registrar_dueno, name='registrar_dueno'),
    path('recepcion/registrar-mascota/', views.registrar_mascota, name='registrar_mascota'),
    # Funcionalidades operador
    path('reservas/<int:reserva_id>/equipo/', views.asignar_equipo_domicilio, name='asignar_equipo_domicilio'),
    #funcionalidades profesionales
    path('profesionales/crear-ficha/', views.crear_ficha_medica, name='crear_ficha_medica'),
    path('profesionales/exito-ficha/', TemplateView.as_view(template_name='pages/profesionales/exito.html'), name='exito_ficha'),
    path('profesionales/ficha/<int:ficha_id>/entrada/', views.crear_entrada, name='crear_entrada'),
]