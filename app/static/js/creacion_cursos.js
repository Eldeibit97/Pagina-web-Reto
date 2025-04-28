let url;
let idCurso;

function pedirImagen() {
  url = prompt("Introduce la URL de la imagen:");
  if (url) {
    mostrarImagen(url);
  }
}

function mostrarImagen(url) {
  let img = document.getElementById("imagen");
  img.src = url;
  img.style.display = "block";
  document.getElementById("btnImagen").textContent = "✎";
}

// Validar que se hayan ingresado todos los datos
function validarDatos() {
  let nombre = document.getElementById("course-name").value.trim();
  let descripcion = document.getElementById("description").value.trim();
  let imagen = document.getElementById("imagen").src;
  
  if (!nombre || !descripcion || !imagen) {
    alert("Ingresa todos los datos necesarios");
    return; // No avanza si falta alguno
  }

  sessionStorage.setItem('courseName', nombre);
  sessionStorage.setItem('courseDesc', descripcion);
  sessionStorage.setItem('courseImage', imagen);
  
  // Si todos los campos están completos, redirige a la siguiente página
  if (idCurso) {
    window.location.href = '/editar_modulo_form/'+ idCurso;
  } else {
    window.location.href = "/crear_modulo_form";
  }
}

window.onload = function () {
  idCurso = document.getElementById("curso-id").value;
  sessionStorage.setItem("IDCurso", idCurso);

  if (idCurso) {
    document.getElementById("form-title").innerText = "Editar Curso";
    document.getElementById("course-name").value = document.getElementById("curso-nombre").value;
    document.getElementById("description").value = document.getElementById("curso-descripcion").value;
    mostrarImagen(document.getElementById("curso-imagen").value);
  } else {
    document.getElementById("form-title").innerText = "Nuevo Curso";
  }
};