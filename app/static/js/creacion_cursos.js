function pedirImagen() {
  let url = prompt("Introduce la URL de la imagen:");
  if (url) {
    localStorage.setItem("imagenURL", url);
    mostrarImagen(url);
    // Cambiar el icono del botón a lápiz
    document.getElementById("btnImagen").textContent = "✎";
  }
}

function mostrarImagen(url) {
  let img = document.getElementById("imagen");
  img.src = url;
  img.style.display = "block";
}

// Validar que se hayan ingresado todos los datos
function validarDatos() {
  let nombre = document.getElementById("course-name").value.trim();
  let descripcion = document.getElementById("description").value.trim();
  let imagen = localStorage.getItem("imagenURL");
  
  if (!nombre || !descripcion || !imagen) {
    alert("Ingresa todos los datos necesarios");
    return; // No avanza si falta alguno
  }

  sessionStorage.setItem('courseName', nombre);
  sessionStorage.setItem('courseDesc', descripcion);
  sessionStorage.setItem('courseImage', imagen);
  
  // Si todos los campos están completos, redirige a la siguiente página
  console.log('clicked');
  window.location.href = "/crear_modulo_form";
}


// Al cargar la página, se verifica si hay una imagen guardada y se muestra
window.onload = function () {
  let urlGuardada = localStorage.getItem("imagenURL");
  if (urlGuardada) {
    mostrarImagen(urlGuardada);
    document.getElementById("btnImagen").textContent = "✎";
  }
};