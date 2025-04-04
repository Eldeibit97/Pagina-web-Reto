let modulos = [];
    let moduloEnEdicion = null;

    const listaModulosView = document.getElementById('listaModulosView');
    const edicionModuloView = document.getElementById('edicionModuloView');
    const listaModulosUl = document.getElementById('lista-modulos');
    const btnAgregarModulo = document.getElementById('btnAgregar');
    const btnListo = document.getElementById('btnListo');
    tituloEdicion = document.getElementById('tituloEdicion');
    const contenedorTarjetas = document.getElementById('contenedorTarjetas');
    const btnAgregarTarjeta = document.getElementById('btnAgregarTarjeta');
    const btnGuardar = document.getElementById('btnGuardar');

    // Agregar un nuevo módulo
    btnAgregarModulo.addEventListener('click', () => {
      const nombreModulo = prompt('¿Qué módulo deseas agregar?');
      if (nombreModulo && nombreModulo.trim() !== '') {
        modulos.push({ nomModulo: nombreModulo.trim(), tarjetas: [] });
        renderizarListaModulos();
      }
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

    // Renderizar la lista de módulos
    function renderizarListaModulos() {
      listaModulosUl.innerHTML = '';
      modulos.forEach((mod, index) => {
        const li = document.createElement('li');
        li.textContent = mod.nomModulo;
        
        const contenedorAcciones = document.createElement('div');
        contenedorAcciones.classList.add('contenedor-acciones');

        const btnEditar = document.createElement('button');
        btnEditar.classList.add('editar');
        btnEditar.innerHTML = '✎';
        btnEditar.addEventListener('click', () => editarModulo(index));
        
        const btnBorrar = document.createElement('button');
        btnBorrar.classList.add('borrar');
        btnBorrar.innerHTML = '🗑️';
        btnBorrar.addEventListener('click', () => {
          modulos.splice(index, 1);
          renderizarListaModulos();
        });
        
        contenedorAcciones.appendChild(btnEditar);
        contenedorAcciones.appendChild(btnBorrar);
        li.appendChild(contenedorAcciones);
        listaModulosUl.appendChild(li);
      });
    }

    // Iniciar la edición del módulo
    function editarModulo(indiceModulo) {
      moduloEnEdicion = indiceModulo;
      const modulo = modulos[indiceModulo];
      tituloEdicion.textContent = `Editar módulo de: ${modulo.nomModulo}`;
      contenedorTarjetas.innerHTML = '';//llllll
      modulo.tarjetas.forEach(agregarTarjetaDOM);
      listaModulosView.classList.add('oculto');
      edicionModuloView.classList.remove('oculto');
    }

    // Agregar una nueva tarjeta al módulo
    btnAgregarTarjeta.addEventListener('click', () => {
      if (moduloEnEdicion === null) return;
      const modulo = modulos[moduloEnEdicion];
      const nuevaTarjeta = { nomTarjeta: "", tipoArchivo: "", videoUrl: "", pregunta: "" };
      modulo.tarjetas.push(nuevaTarjeta);
      agregarTarjetaDOM(nuevaTarjeta);
    });

    // Crear y agregar una tarjeta al DOM
    function agregarTarjetaDOM(tar) {
      const divTarjeta = document.createElement('div');
      divTarjeta.classList.add('tarjeta');
      
      const inputTitulo = document.createElement('input');
      inputTitulo.type = 'text';
      inputTitulo.placeholder = 'Type the Name of this tarjeta...';
      inputTitulo.value = tar.nomTarjeta;
      inputTitulo.addEventListener('input', (e) => {
        tar.nomTarjeta = e.target.value;
      });
      divTarjeta.appendChild(inputTitulo);

      const mediaContainer = document.createElement('div');
      mediaContainer.classList.add('media-container');
      
      const botones = [
        { tipoArchivo: 'lectura', icono: '📘', campo: 'lecturaText', promptMsg: 'Introduce el contenido de la lectura:' },
        { tipoArchivo: 'video', icono: '▶️', campo: 'videoUrl', promptMsg: 'Introduce la URL del video:' },
        { tipoArchivo: 'cuestionario', icono: '📝', campo: 'pregunta', promptMsg: 'Introduce la pregunta:' }
      ];

      let botonesDOM = [];

      botones.forEach(({ tipoArchivo, icono, campo, promptMsg }) => {
        const boton = document.createElement('button');
        boton.classList.add('upload-icon');
        boton.innerHTML = tar[campo] ? (campo === 'tipoArchivo' ? `<img src="${tar[campo]}" alt="" style="width:24px;height:24px;border-radius:4px;">` : '📹') : icono;
        
        boton.addEventListener('click', () => {
          botonesDOM.forEach(btn => btn.style.display = 'inline-block');
          if (tar[campo]) {
            tar[campo] = "";
            boton.innerHTML = icono;
          } else {
            const valor = prompt(promptMsg);
            if (valor && valor.trim() !== '') {
              tar[campo] = valor.trim();
              tar.tipoArchivo = tipoArchivo;
              boton.innerHTML = campo === 'tipoArchivo' ? `<img src="${tar[campo]}" alt="" style="width:24px;height:24px;border-radius:4px;">` : '✅';
              botonesDOM.forEach(btn => { if (btn !== boton) btn.style.display = 'none'; });
            }
          }
        });
        mediaContainer.appendChild(boton);
        botonesDOM.push(boton);
      });

      divTarjeta.appendChild(mediaContainer);
      contenedorTarjetas.appendChild(divTarjeta);
    }

    // Guardar los cambios
    btnGuardar.addEventListener('click', () => {
      alert('Cambios guardados (demo).');
      console.log(JSON.stringify(modulos, null, 2));

      edicionModuloView.classList.add('oculto');
      listaModulosView.classList.remove('oculto');
      renderizarListaModulos();
    });

    // Enviar los datos al servidor
    btnListo.addEventListener('click', () => {
      crearNuevaCurso();
      alert('Botón Listo presionado (pendiente de implementar).');
    });

    // Renderizar la lista al inicio
    renderizarListaModulos();
