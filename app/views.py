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
        mascotas = None
        recetas = None
    elif tipo == 'operador':
        reservas = Reserva.objects.filter(tipo_reserva='domicilio')
        mascotas = None
        recetas = None
    elif tipo in ['veterinario', 'estilista']:
        mascotas = Mascota.objects.select_related('dueno').all()
        reservas = None
        recetas = None
    elif tipo == 'ventas':
        rut = request.GET.get('rut')
        receta_id = request.GET.get('receta_id')
        recetas = Receta.objects.select_related(
            'entrada__ficha_medica__mascota__dueno'
        ).all().order_by('-fecha')
        if rut:
            recetas = recetas.filter(entrada__ficha_medica__mascota__dueno__rut__icontains=rut)
        if receta_id:
            recetas = recetas.filter(id=receta_id)
        reservas = None
        mascotas = None
    else:
        reservas = None
        mascotas = None
        recetas = None

    context = {
        'tipo_usuario': tipo,
        'reservas': reservas if tipo in ['recepcion', 'operador'] else None,
        'mascotas': mascotas if tipo in ['veterinario', 'estilista'] else None,
        'recetas': recetas if tipo == 'ventas' else None,
        'filtro_rut': request.GET.get('rut', ''),
        'filtro_receta_id': request.GET.get('receta_id', ''),
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

@login_required
def ver_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    ficha = getattr(mascota, 'fichamedica', None)
    entradas = []
    ultimo_peso = None

    # Filtrado por fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if ficha:
        entradas = ficha.entradas.all().order_by('-fecha')
        if fecha_inicio:
            entradas = entradas.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            entradas = entradas.filter(fecha__date__lte=fecha_fin)
        ultima_entrada = ficha.entradas.order_by('-fecha').first()
        if ultima_entrada:
            ultimo_peso = ultima_entrada.peso

    context = {
        "mascota": mascota,
        "ficha": ficha,
        "entradas": entradas,
        "ultimo_peso": ultimo_peso,
        "fecha_inicio": fecha_inicio or "",
        "fecha_fin": fecha_fin or "",
    }
    return render(request, "pages/ver_mascota.html", context)

@login_required
def ver_dueno(request):
    return render(request, "pages/ver_dueno.html")

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
    
@login_required
def ver_mis_mascotas(request):
    if request.user.tipo_usuario != 'cliente':
        return HttpResponseForbidden("Acceso denegado.")
    mascotas = Mascota.objects.filter(dueno__usuario=request.user)
    return render(request, 'pages/cliente/mascotas.html', {'mascotas': mascotas})
    
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
    especie_choices = Mascota.ESPECIE_CHOICES
    return render(request, 'pages/recepcion/registro_mascota.html', {
        'duenos': duenos,
        'sexo_choices': sexo_choices,
        'especie_choices': especie_choices,
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

""" ------------------------------------------------------------------ """
# funcionalidades Veterinario y estilista

@login_required
def crear_ficha_medica(request):
    mascota_id = request.GET.get("mascota_id")
    if mascota_id:
        mascota = get_object_or_404(Mascota, id=mascota_id)
        if not hasattr(mascota, 'fichamedica'):
            FichaMedica.objects.create(mascota=mascota)
    return redirect('panel')

@login_required
def crear_entrada(request, ficha_id):
    ficha = get_object_or_404(FichaMedica, id=ficha_id)
    if request.method == "POST":
        peso = request.POST.get("peso")
        descripcion = request.POST.get("descripcion")
        tratamiento = request.POST.get("tratamiento")  # Nuevo campo
        entrada = Entrada.objects.create(
            ficha_medica=ficha,
            peso=peso,
            descripcion=descripcion,
            tratamiento=tratamiento
        )
        # Solo veterinario puede crear receta
        if request.user.tipo_usuario == 'veterinario' and request.POST.get("tiene_receta"):
            medicamentos = request.POST.get("medicamentos")
            indicaciones_generales = request.POST.get("indicaciones_generales")
            Receta.objects.create(
                entrada=entrada,
                medicamentos=medicamentos,
                indicaciones_generales=indicaciones_generales,
                firmado_por=request.user
            )
        return redirect('ver_mascota', mascota_id=ficha.mascota.id)
    return render(request, "pages/profesionales/crear_entrada.html", {"ficha": ficha})