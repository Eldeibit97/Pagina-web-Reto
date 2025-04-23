/*↓ ------------codigo para la funcionalidad global-----------------↓*/
let modulos = [];

const listaModulosView = document.getElementById('listaModulosView'); //screen for modules
const edicionModuloView = document.getElementById('edicionModuloView'); //screen for contents of the module
const edicionLecturaView = document.getElementById('edicionLecturaView');//screen for reading editing

let Indice_ModuloEnEdicion;

let idCurso;


/*↓ ------------codigo para la pantalla del lista del modulo-----------------↓*/
const listaModulos = document.getElementById('lista-modulos');
const btnAgregarModulo = document.getElementById('btnAgregarModulo');
const btnListo = document.getElementById('btnListo');

//functiona para agregar un nuevo modulo
function agregarModulo(nombreModulo = '' ) {
    const li = document.createElement('li');//module box
    const input = document.createElement('input');//text holder
    input.classList.add('inputModule');
    input.type = 'text';
    input.placeholder = 'Ingresa el nombre del modulo...';
    input.value = nombreModulo;
    li.appendChild(input);

    //✎button
    const btnEditar = document.createElement('button');
    btnEditar.classList.add('editarButton');
    btnEditar.innerHTML = 'Contenido✎';
    btnEditar.title = 'Editar los contenidos de este modulo.'
    btnEditar.addEventListener('click', () => {
        if (input.value === ''){
            alert('Tienes que ingresar el nombre de este modulo');
        }
        else {
            if (!modulos.some(modulo => modulo.nomModulo === input.value.trim())){
                const nuevoModulo = {
                    nomModulo: input.value.trim(),
                    contenidos: []
                };
                modulos.push(nuevoModulo);
            }
            Indice_ModuloEnEdicion = Array.from(li.parentElement.children).indexOf(li);
            const tituloEdicion = document.getElementById('tituloEdicion');
            tituloEdicion.textContent = `Editar Modulo: ${modulos[Indice_ModuloEnEdicion].nomModulo}`;
            listaModulosView.classList.add('oculto');
            edicionModuloView.classList.remove('oculto');
            renderizarTarjetas();
        }
    })

    //🗑️button
    const btnBorrar = document.createElement('button');
    btnBorrar.classList.add('borrarButton');
    btnBorrar.innerHTML = '🗑️';
    btnBorrar.title = 'Borrar este moduloEnEdicion.'
    btnBorrar.addEventListener('click', () => {
        if (modulos.some(modulo => modulo.nomModulo === input.value.trim())){ // if this module had been edited last time
            
            const borrarConfirmacion = confirm('¿Estás seguro de que quieres borrar este modulo?\nLos contenidos que editaste se eliminarán.')
            if (!borrarConfirmacion) return;
            
            const index = modulos.findIndex(modulo => modulo.nomModulo === input.value.trim());
            if (index !== -1) {
                modulos.splice(index, 1);
            }
        }
        li.remove();
    })

    //make a container for ✎button and 🗑️button
    const contenedorButtones = document.createElement('div');
    contenedorButtones.classList.add('contenedor-acciones');
    contenedorButtones.appendChild(btnEditar);
    contenedorButtones.appendChild(btnBorrar);

    li.appendChild(contenedorButtones);
    listaModulos.appendChild(li);

    //detect the case when some inputs have same value
    const inputs = document.querySelectorAll('input');

    inputs.forEach(input => {
        const errorMsg = document.createElement('div');
        errorMsg.classList.add('error-msg');
        errorMsg.style.color = 'red';
        errorMsg.style.fontSize = '0.5em';
        errorMsg.style.display = 'none';
        input.parentNode.insertBefore(errorMsg, input.nextSibling);

        input.addEventListener('input', () => {
            const currentValue = input.value.trim();
            const isDuplicated = Array.from(inputs).some(otherInput => 
            otherInput !== input && otherInput.value.trim() === currentValue
            );

            if (isDuplicated) {
            input.style.border = '4px solid red';
            errorMsg.textContent = "Este nombre ya ha sido utilizado.";
            errorMsg.style.display = 'block';
            btnEditar.disabled = true;
            } else {
            input.style.border = '';
            errorMsg.textContent = "";
            errorMsg.style.display = 'none';
            btnEditar.disabled = false;
            }
        });
    });
}

// Agregar un nuevo módulo (this button works as template duplicator)
btnAgregarModulo.addEventListener('click', () => agregarModulo());

// función para actualizar y volver a mostrar la información del módulo.
function renderizarListaModulos() {
    listaModulos.innerHTML = '';
    modulos.forEach(modulo => {
        agregarModulo(modulo.nomModulo);
    });
}


/*↓ ------------codigo para la pantalla para edtar los contenidos del modulo-----------------↓*/
const contenedorTarjetas = document.getElementById('contenedorTarjetas');
const btnAgregarTarjeta = document.getElementById('btnAgregarTarjeta');
let Indice_TarjetaEnEdicion;

function agregarTarjeta(nombreTarjeta = ''){
    const divTarjeta = document.createElement('div');//tarjeta box
    divTarjeta.classList.add('tarjeta');
    
    // ✖button
    const btnCerrar = document.createElement('button');
    btnCerrar.classList.add('btn-cerrar');
    btnCerrar.innerHTML = '✖';
    btnCerrar.title = 'Borrar este Tarjeta';
    btnCerrar.addEventListener('click', () => {
        if (modulos[Indice_ModuloEnEdicion].contenidos.some(contenido => contenido.nomContenido === inputTarjeta.value.trim())){ // if this contents had been edited last time
            
            const borrarConfirmacion = confirm('¿Estás seguro de que quieres borrar este contenido?\nLos contenidos que editaste se eliminarán.')
            if (!borrarConfirmacion) return;
            
            const index = modulos[Indice_ModuloEnEdicion].contenido.findIndex(contenido => contenido.nomContenido === inputTarjeta.value.trim());
            if (index !== -1) {
                modulos[Indice_ModuloEnEdicion].contenido.splice(index, 1);
            }
        }
        divTarjeta.remove();
    });

    divTarjeta.appendChild(btnCerrar);

    const inputTarjeta = document.createElement('input');
    inputTarjeta.classList.add('inputTarjeta');
    inputTarjeta.type = 'text';
    inputTarjeta.placeholder = 'Type the Name of this tarjeta...';
    inputTarjeta.value = nombreTarjeta;
    divTarjeta.appendChild(inputTarjeta);
    
    const mediaContainer = document.createElement('div'); // three icons container(📘, ▶️, 📝)
    mediaContainer.classList.add('media-container');

    const botones = [
        { tipoArchivo: 'lectura', icono: '📘', campo: 'lecturaTexto', titulo: "Agregar un nueva LECTURA", checker:0},
        { tipoArchivo: 'video', icono: '▶️', campo: 'videoUrl', titulo: "Agregar un nueva VIDEO", checker:0},
        { tipoArchivo: 'cuestionario', icono: '📝', campo: 'pregunta', titulo: "Agregar un nueva CUESTIONARIO", checker:0}
    ];

    

    function tieneContenidoValido(contenido, campo) {
      const valor = contenido[campo];
      return Array.isArray(valor) ? valor.length > 0 : !!(valor && valor.trim && valor.trim() !== '');
    }
    
    botones.forEach(({tipoArchivo, icono, campo, titulo, checker    })=> {
        const boton = document.createElement('button');
        boton.classList.add('upload-icon');
        boton.innerHTML = icono;
        boton.title = titulo;

        mediaContainer.appendChild(boton);

        let contenidoActual = modulos[Indice_ModuloEnEdicion]?.contenidos || [];
        let contenidoGuardado = contenidoActual.find(
          contenido => contenido.nomContenido == inputTarjeta.value && contenido.tipo === tipoArchivo && tieneContenidoValido(contenido, campo)
        );

        if (contenidoGuardado) {
          boton.innerHTML = '✅';
          contenidoGuardado = null;
          
        }
        

        boton.addEventListener('click', () => {
            if (inputTarjeta.value.trim() === ''){
                alert('Tienes que ingresar el titulo');
            }
            else {
                if (!modulos[Indice_ModuloEnEdicion].contenidos.some(contenido => contenido.nomContenido === inputTarjeta.value.trim())){ // if there is already saved value in modulos
                    const nuevoContenido = {
                        nomContenido: inputTarjeta.value.trim(),
                        tipo: tipoArchivo,
                        [campo]: [],
                        checker: 1
                    };
                    modulos[Indice_ModuloEnEdicion].contenidos.push(nuevoContenido);
                    Indice_TarjetaEnEdicion = modulos[Indice_ModuloEnEdicion].contenidos.length - 1;
                }
                else{
                    Indice_TarjetaEnEdicion = modulos[Indice_ModuloEnEdicion].contenidos.findIndex(contenido => contenido.nomContenido === inputTarjeta.value.trim());
                }

                if (tipoArchivo == 'lectura') {
                    edicionModuloView.classList.add('oculto');
                    edicionLecturaView.classList.remove('oculto');
                    renderizarPaginas();
                }
                else if (tipoArchivo == 'video'){
                    videoUrl = prompt('Introduce la URL del video:')
                    if (videoUrl && Indice_TarjetaEnEdicion !== -1) {
                        modulos[Indice_TarjetaEnEdicion].contenidos[Indice_TarjetaEnEdicion][campo] = videoUrl;
                    }
                }
                else if (tipoArchivo == 'cuestionario'){
                  sessionStorage.setItem('modulos', JSON.stringify(modulos));
                  sessionStorage.setItem('Indice_ModuloEnEdicion', Indice_ModuloEnEdicion);
                  sessionStorage.setItem('Indice_TarjetaEnEdicion', Indice_TarjetaEnEdicion);
                  window.location.href = "/crear_cuestionario_form";
                }

                boton.innerHTML = '✅';
                mediaContainer.querySelectorAll('button').forEach(btn => {
                    if (btn !== boton) btn.style.display = 'none';
                });
            }
        })
    })
    const botonesEnContenedor = mediaContainer.querySelectorAll('button');

    const botonCheckeado = Array.from(botonesEnContenedor).find(btn => btn.innerHTML === '✅');

    if (botonCheckeado) {
      botonesEnContenedor.forEach(btn => {
        if (btn !== botonCheckeado) btn.style.display = 'none';
      });
    }
    divTarjeta.appendChild(mediaContainer);
    contenedorTarjetas.appendChild(divTarjeta);

    //detect the case when some inputs have same value
    const inputs = document.querySelectorAll('.inputTarjeta');

    inputs.forEach(input => {
        const errorMsg = document.createElement('div');
        errorMsg.classList.add('error-msg');
        errorMsg.style.color = 'red';
        errorMsg.style.fontSize = '0.5em';
        errorMsg.style.display = 'none';
        input.parentNode.insertBefore(errorMsg, input.nextSibling);

        input.addEventListener('input', () => {
            const currentValue = input.value.trim();
            const isDuplicated = Array.from(inputs).some(otherInput => 
                otherInput !== input && otherInput.value.trim() === currentValue
            );

            if (isDuplicated) {
                input.style.border = '4px solid red';
                errorMsg.textContent = "Este nombre ya ha sido utilizado.";
                errorMsg.style.display = 'block';
                mediaContainer.querySelectorAll('button').forEach(btn => {
                    btn.disabled = true;
                })
            } else {
                input.style.border = '';
                errorMsg.textContent = "";
                errorMsg.style.display = 'none';
                mediaContainer.querySelectorAll('button').forEach(btn => {
                    btn.disabled = false;
                })
            }
        });
    });
}
btnAgregarTarjeta.addEventListener('click', () => agregarTarjeta());

// función para actualizar y volver a mostrar la información del tarjetas.
function renderizarTarjetas(){
    contenedorTarjetas.innerHTML = '';
    
    modulos[Indice_ModuloEnEdicion].contenidos.forEach(contenido => {
        agregarTarjeta(contenido.nomContenido);
    });
}

// Guardar los cambios
const btnGuardarTarjeta = document.getElementById('btnGuardarTarjeta');
btnGuardarTarjeta.addEventListener('click', () => {
    alert('Cambios guardados');

    edicionModuloView.classList.add('oculto');
    listaModulosView.classList.remove('oculto');
    renderizarListaModulos();
})


/*↓ ------------codigo para la pantalla de Lectura-----------------↓*/
const btnAnadirPag = document.getElementById('btnAnadirPag');
const btnGuardarPag = document.getElementById('btnGuardarPag');
const contenedorPaginas = document.getElementById('contenedorPaginas');

function agregarPagina(nombrePagina = '', textoPagina = '', imgPagina = ''){
  const nuevaPagina = document.createElement('div');
  nuevaPagina.classList.add('pagina');

  const tituloContainer = document.createElement('div');
  tituloContainer.classList.add('titulo-container');

  const tituloInput = document.createElement('input');
  tituloInput.type = 'text';
  tituloInput.placeholder = 'Titulo de este pagina';
  tituloInput.value = nombrePagina;

  tituloContainer.appendChild(tituloInput);
  nuevaPagina.appendChild(tituloContainer);

  const texto = document.createElement('textarea');
  texto.placeholder = 'Texto de la página...';
  texto.value = textoPagina;
  texto.classList.add('contenido-texto');
  nuevaPagina.appendChild(texto);

  const botonImagen = document.createElement('button');
  botonImagen.classList.add('imagen-btn');
  botonImagen.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
    <path d="M21 19V5H3v14h18zM3 3h18c1.1 0 2 .9 2 2v14c0 1.1-.9 2-2 2H3
      c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2zm10 14l-2.03-2.71-2.97 3.71H21l-4-5z"/>
  </svg>`;
  
  let img = document.createElement('img');
  nuevaPagina.appendChild(img);
  if (imgPagina){
    img.src = imgPagina
  };
  

  botonImagen.addEventListener('click', () => {
    const urlImagen = prompt("Introduce la URL de una imagen en internet:");
    if (urlImagen && urlImagen.trim() !== "") {
      img.src = urlImagen;
      img.style.maxWidth = "100%";
      img.style.marginTop = "10px";
      img.style.borderRadius = "4px";
    }
  });
  
    nuevaPagina.appendChild(botonImagen);
  
    contenedorPaginas.appendChild(nuevaPagina);
}

btnAnadirPag.addEventListener('click', () => agregarPagina());

function renderizarPaginas(){
  contenedorPaginas.innerHTML = '';

  modulos[Indice_ModuloEnEdicion].contenidos[Indice_TarjetaEnEdicion].lecturaTexto.forEach(pagina => {
    agregarPagina(pagina.nomPagina, pagina.texto, pagina.imgPagina);
  })
}

btnGuardarPag.addEventListener('click', () => {
  const paginas = document.querySelectorAll('.pagina');
  const lecturaTexto = [];

  let faltaTitulo = false;

  paginas.forEach(pagina => {
    // Título puede estar en un <h2> si ya fue confirmado, o en un <input>
    let tituloElem = pagina.querySelector('.titulo-container h2') || pagina.querySelector('.titulo-container input');
    const titulo = tituloElem ? tituloElem.value || tituloElem.textContent : '';

    if (!titulo || titulo.trim() === '') {
      faltaTitulo = true;
      return;
    }

    const texto = pagina.querySelector('textarea')?.value || '';
    const img = pagina.querySelector('img')?.src || '';

    lecturaTexto.push({
      nomPagina: titulo.trim(),
      texto: texto.trim(),
      imgPagina: img
    });
  });

  if (faltaTitulo) {
    alert("Tienes que ingresar todos los títulos.");
    return;
  }

  // Ahora guardamos en el objeto deseado:
  modulos[Indice_ModuloEnEdicion].contenidos[Indice_TarjetaEnEdicion].lecturaTexto = lecturaTexto;

  alert("¡Contenido guardado exitosamente!");
  
  // Back to module view
  edicionLecturaView.classList.add('oculto');
  listaModulosView.classList.remove('oculto');
});
  


    
// Enviar los datos al servidor
function crearNuevaCurso() {
  const courseNombre = sessionStorage.getItem("courseName");
  const courseDescripcion = sessionStorage.getItem("courseDesc");
  const courseImagen_url = sessionStorage.getItem("courseImage");
  
  fetch('/crear_curso', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ courseNombre, courseDescripcion, courseImagen_url, modulos })
  })
  .then(response => response.json())
  .then(data => alert(data.message))
  .catch(error => console.error('Error:', error));
}

function editarCurso(){
  const courseNombre = sessionStorage.getItem("courseName");
  const courseDescripcion = sessionStorage.getItem("courseDesc");
  const courseImagen_url = sessionStorage.getItem("courseImage");
  
  fetch('/editar_curso', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({idCurso, courseNombre, courseDescripcion, courseImagen_url, modulos })
  })
  .then(response => response.json())
  .then(data => alert(data.message))
  .catch(error => console.error('Error:', error));
}


// Enviar los datos al servidor
btnListo.addEventListener('click', () => {
  if (idCurso) {
    editarCurso();
  }
  else{
    crearNuevaCurso();
  }
});

window.onload = () => {
  modulos = []
  idCurso = sessionStorage.getItem('IDCurso');
  
  if(idCurso){
    fetch(`/api/obtener_curso/${idCurso}`)
      .then(response => response.json())
      .then(data => {
        modulos = data.modulos;
        document.getElementById('modulo-header').innerText="Editar Modulo";
        renderizarListaModulos();
      })
      .catch(error => {
        console.error("Error al obtener el curso:", error);
      });

    
    
  } else{
    document.getElementById('modulo-header').innerText="Crear Modulo";
    renderizarListaModulos();
  }

  const storedModulos = JSON.parse(sessionStorage.getItem('modulos'));

  if (storedModulos) {
    modulos = storedModulos;
    sessionStorage.removeItem('modulos');
    renderizarListaModulos();

    const cuestionarioData = JSON.parse(sessionStorage.getItem("cuestionarioData"));

    sessionStorage.removeItem('cuestionarioData');

    Indice_ModuloEnEdicion = sessionStorage.getItem('Indice_ModuloEnEdicion');
    Indice_TarjetaEnEdicion = sessionStorage.getItem('Indice_TarjetaEnEdicion');

    if (cuestionarioData) {
        modulos[Indice_ModuloEnEdicion].contenidos[Indice_TarjetaEnEdicion].pregunta = cuestionarioData.preguntas;
    }
    console.log("✅ After merged modulos:", modulos);
  }
  
};
