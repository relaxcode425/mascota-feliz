document.addEventListener("DOMContentLoaded", function () {
const tipoReserva = document.querySelector('select[name="tipo_reserva"]');
const direccion = document.getElementById('campo-direccion');

if (tipoReserva){
    tipoReserva.addEventListener("change", function () {
    if (this.value === "domicilio") {
    direccion.style.display = "block";
    } else {
    direccion.style.display = "none";
    }
});
}

});