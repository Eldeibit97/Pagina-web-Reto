let url;
let idCurso;
const container = document.getElementById("container");
const input = document.querySelector('.imageInput');
const imageDisplay = document.querySelector('.imagePreview');
imageDisplay.classList.add('img');

let base64Image = '';

input.addEventListener('change', () => {
  if (input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      imageDisplay.src = e.target.result;
      imageDisplay.style.display = 'block';
      base64Image = e.target.result;
    };
    reader.readAsDataURL(input.files[0]);
  }
});

function mostrarImagen(url) {
  let img = document.getElementById("imagePreview");
  img.src = url;
  img.style.display = "block";
}

// Validar que se hayan ingresado todos los datos
function validarDatos() {
  let nombre = document.getElementById("course-name").value.trim();
  let descripcion = document.getElementById("description").value.trim();
  let img = container.querySelector("img")?.src || "";
  if (!nombre || !descripcion) {
    alert("Ingresa todos los datos necesarios");
    return; // No avanza si falta alguno
  }

  // sessionStorage.setItem('courseName', nombre);
  // sessionStorage.setItem('courseDesc', descripcion);
  // sessionStorage.setItem('courseImage', img);
  
  
  // Si todos los campos están completos, redirige a la siguiente página
  if (idCurso) {
    fetch('/editar_curso', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({idCurso, nombre, descripcion, img })
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);;
    })
    .catch(error => console.error('Error:', error));
    window.location.href = '/cursos';
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
    
    console.log(document.getElementById("curso-imagen").value);
    mostrarImagen(document.getElementById("curso-imagen").value);
  
  } else {
    document.getElementById("form-title").innerText = "Crear un nuevo Curso";
  }
};