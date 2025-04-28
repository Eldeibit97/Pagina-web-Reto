const confirmacion = document.getElementById("eliminar");
const botones_eliminar = document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target="#delete_modal"]')

botones_eliminar.forEach(button =>{
  button.addEventListener('click', function() {
    const href = this.getAttribute('data-url');
    const alumno = this.getAttribute('data-id');
    confirmacion.setAttribute('href', href);
    document.getElementById("modal_body").innerHTML = "Estas seguro que quieres eliminar al alumno?<br><br><b>"+ alumno +"</b><br><br>(una vez <b>eliminado no hay vuelta atras</b>)";
  });
});