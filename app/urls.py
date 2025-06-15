from django.urls import path, include
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path('panel/', views.panel_principal, name='panel'),
    path('logout/', views.logout_view, name='logout'),
    path('reservar/', views.reservar_servicio, name='reservar_servicio'),
    path('reservar/fecha/', views.seleccionar_fecha, name='seleccionar_fecha'),
    path('reservar/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservar/exito/', TemplateView.as_view(template_name='pages/cliente/reserva_exitosa.html'), name='reserva_exitosa'),
]