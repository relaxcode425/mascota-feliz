from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta, datetime, date
from core.models import *
from core.forms import *

""" ------------------------------------------------------------------ """

# Create your views here.
def index(request):
    context = {}
    return render(request, "pages/index.html", context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('panel')  # redirige siempre al panel único
        else:
            messages.error(request, 'Credenciales inválidas')
    return render(request, 'pages/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

""" ------------------------------------------------------------------ """
#Panel según usuario

@login_required
def panel_principal(request):
    tipo = request.user.tipo_usuario

    if tipo == 'recepcion':
        reservas = Reserva.objects.filter(tipo_reserva='presencial')
    if tipo == 'operador':
        reservas = Reserva.objects.filter(tipo_reserva='domicilio')

    context = {
        'tipo_usuario': tipo,
        'reservas': reservas if tipo in ['recepcion', 'operador'] else None,
    }

    return render(request, 'pages/panel_general.html', context)

@login_required
def ver_reservas_cliente(request):
    if request.user.tipo_usuario != 'cliente':
        return HttpResponseForbidden("Acceso denegado.")
    
    reservas = Reserva.objects.filter(cliente=request.user).order_by('-fecha', '-hora')
    return render(request, 'pages/ver_reservas.html', {
        'reservas': reservas,
        'today': date.today()
    })

""" ------------------------------------------------------------------ """
# funcionalidades cliente

@login_required
def reservar_servicio(request):
    if request.user.tipo_usuario != 'cliente':
        return HttpResponseForbidden("Acceso denegado.")

    if request.method == 'POST':
        tipo_servicio = request.POST.get('tipo_servicio')
        tipo_reserva = request.POST.get('tipo_reserva')

        if tipo_servicio and tipo_reserva:
            # Guardar selección temporalmente (en sesión)
            request.session['reserva_datos'] = {
                'tipo_servicio': tipo_servicio,
                'tipo_reserva': tipo_reserva,
            }
            return redirect('seleccionar_fecha')

    return render(request, 'pages/cliente/reservar.html')

def seleccionar_fecha(request):
    if request.user.tipo_usuario != 'cliente':
        return HttpResponseForbidden("Acceso denegado.")

    reserva_datos = request.session.get('reserva_datos')
    if not reserva_datos:
        return redirect('reservar_servicio')

    # Fechas y horarios disponibles (más adelante generar desde la BD)
    hoy = timezone.now().date()
    dias_disponibles = [hoy + timedelta(days=i) for i in range(1, 6)]
    horas_disponibles = ['09:00', '11:00', '13:00', '15:00', '17:00']

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        if fecha and hora:
            reserva_datos['fecha'] = fecha
            reserva_datos['hora'] = hora
            request.session['reserva_datos'] = reserva_datos
            return redirect('confirmar_reserva')

    return render(request, 'pages/cliente/seleccionar_fecha.html', {
        'dias_disponibles': dias_disponibles,
        'horas_disponibles': horas_disponibles
    })

@login_required
def confirmar_reserva(request):
    if request.user.tipo_usuario != 'cliente':
        return HttpResponseForbidden("Acceso denegado.")

    datos = request.session.get('reserva_datos')
    if not datos:
        return redirect('reservar_servicio')

    if request.method == 'POST':

        direccion = datos.get("direccion") if datos['tipo_reserva'] == "domicilio" else None

        Reserva.objects.create(
            cliente=request.user,
            tipo_servicio=datos['tipo_servicio'],
            tipo_reserva=datos['tipo_reserva'],
            fecha=datos['fecha'],
            hora=datetime.strptime(datos['hora'], "%H:%M").time(),
            direccion=direccion,
            estado='pendiente'  # valor por defecto
        )

        del request.session['reserva_datos']  # Limpiar
        return redirect('reserva_exitosa')

    return render(request, 'pages/cliente/confirmar_reserva.html', {
        'datos': datos
    })

@login_required
def cancelar_reserva_cliente(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if request.method == 'POST':
        if reserva.fecha >= date.today():
            reserva.estado = "cancelada"
            reserva.save()
            messages.success(request, "La reserva ha sido cancelada correctamente.")
        else:
            messages.error(request, "No se puede cancelar una reserva pasada.")
        return redirect('ver_reservas_cliente')
    
""" ------------------------------------------------------------------ """
# Funcionalidades recepcion
@login_required
def cambiar_estado_reserva(request, reserva_id, nuevo_estado):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verificación opcional de permisos (solo recepción u operador)
    if request.user.tipo_usuario not in ['recepcion', 'operador']:
        messages.error(request, "No tienes permiso para cambiar el estado de esta reserva.")
        return redirect('panel')

    # Actualizar estado
    reserva.estado = nuevo_estado
    reserva.save()
    messages.success(request, f"Estado actualizado a: {reserva.get_estado_display()}")
    return redirect('panel')

""" @login_required
def registrar_dueno(request):
    if request.method == 'POST':
        form = DuenoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Dueño registrado con éxito.")
            return redirect('panel')
    else:
        form = DuenoForm()
    return render(request, 'recepcion/registrar_dueno.html', {'form': form}) """

def registrar_dueno(request):
    if request.method == "POST":
        return render(request, "pages/recepcion/exito_registro.html", {"mensaje": "dueño"})
    
    return render(request, "pages/recepcion/registro_dueno.html")

def registrar_mascota(request):
    if request.method == "POST":
        return render(request, "pages/recepcion/exito_registro.html", {"mensaje": "mascota"})
    duenos = Dueno.objects.all()
    sexo_choices = Mascota.SEXO_CHOICES
    return render(request, 'pages/recepcion/registro_mascota.html', {
        'duenos': duenos,
        'sexo_choices': sexo_choices,
    })

""" ------------------------------------------------------------------ """  
#Funcionalidades operador

@login_required
def asignar_equipo_domicilio(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, tipo_reserva='domicilio')

    try:
        servicio = ServicioDomicilio.objects.get(reserva=reserva)
    except ServicioDomicilio.DoesNotExist:
        servicio = None

    if request.method == 'POST':
        form = ServicioDomicilioForm(request.POST, instance=servicio)
        if form.is_valid():
            nuevo_servicio = form.save(commit=False)
            nuevo_servicio.reserva = reserva
            nuevo_servicio.save()
            messages.success(request, "Equipo asignado correctamente.")
            return redirect('panel')
    else:
        form = ServicioDomicilioForm(instance=servicio)

    return render(request, 'pages/operador/crear_equipo_movil.html', {
        'reserva': reserva,
        'form': form
    })