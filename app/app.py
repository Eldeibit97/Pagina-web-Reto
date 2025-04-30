from flask import Flask, jsonify, redirect, url_for, request, send_from_directory, render_template, session, Response, send_file
from flask_cors import cross_origin
import operaciones_sql
import os
import re
import ast
import base64
import mimetypes

app = Flask(__name__)
app.secret_key = 'super secret key'

## Funciones ##


# Endpoints

#Videojuego

# Fix MIME types for Unity files
mimetypes.add_type('application/wasm', '.wasm')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/octet-stream', '.data')

@app.route('/game')
def game():
    session['section'] = 'game'
    return render_template('game.html', id_rol = session['id_rol'])  # game.html is your Unity WebGL page

@app.route('/app/static/webgl/Build/<path:filename>')
def serve_build(filename):
    # Full logical file path
    logical_path = os.path.join('static', 'webgl', 'Build', filename)
    
    # Check if there's a compressed version (.br) available
    compressed_path = logical_path + '.br'

    if os.path.exists(compressed_path):
        response = send_file(compressed_path)
        response.headers['Content-Encoding'] = 'br'

        # Set correct Content-Type manually
        if filename.endswith('.wasm'):
            response.headers['Content-Type'] = 'application/wasm'
        elif filename.endswith('.js'):
            response.headers['Content-Type'] = 'application/javascript'
        elif filename.endswith('.data'):
            response.headers['Content-Type'] = 'application/octet-stream'
        else:
            response.headers['Content-Type'] = 'application/octet-stream'
        
        return response
    else:
        # Fallback if uncompressed file exists
        return send_file(logical_path)

@app.route('/get_questions', methods=['GET'])
@cross_origin()
def get_questions():
    try:
        questions = operaciones_sql.get_questions()
        return jsonify({"questions": questions})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_choicequestions', methods=['GET'])
@cross_origin()
def get_choicequestions():
    try:
        questions = operaciones_sql.get_choice_questions()
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#vista de los cursos
@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    if request.method == 'GET':
        if 'username' in session:
            session['section'] = 'cursos'
            id_rol = session['id_rol']
            cursos = operaciones_sql.find_cursos(session['id'])
            if session['id_rol'] == 1:
                return render_template('cursos.html', cursos = cursos, id_rol = id_rol)
            elif session['id_rol'] == 2:
                cursos = operaciones_sql.get_cursos()
                return render_template('cursos.html', cursos = cursos, id_rol = id_rol)
            else:
                cursos = operaciones_sql.get_cursos()
                return render_template('cursos.html', cursos = cursos, id_rol = id_rol)
        else:
            return redirect(url_for('login', fail='False'))
    else:
        
        return redirect(url_for('vista_curso', id_curso=request.form['id_curso']))
    

@app.route('/vista_curso/<id_curso>')
def vista_curso(id_curso):
    if 'username' in session:
        session['section'] = 'vista_curso'
        curso = operaciones_sql.get_curso(id_curso)
        nombre_curso = curso[0]
        descripcion_curso = curso[1]
        id_rol=session['id_rol']

        modulos, progreso = operaciones_sql.get_lecciones(id_curso)
        #print(modulos)

        if session['id_rol'] == 3 or session['id_rol'] == 2:
            asignados, no_asignados = operaciones_sql.get_alumnos_curso(id_curso)
            return render_template('vista_curso.html', id_curso=id_curso, nombre_curso=nombre_curso, descripcion_curso=descripcion_curso, modulos=modulos, progreso=progreso, asignados=asignados, no_asignados = no_asignados, id_rol=id_rol)
        else:
            return render_template('vista_curso.html', id_curso=id_curso, nombre_curso=nombre_curso, descripcion_curso=descripcion_curso, modulos=modulos, progreso=progreso, asignados=None, no_asignados=None, id_rol=id_rol)
    else:
        return redirect(url_for('login', fail='False')) 

#vista de las lecciones
@app.route('/leccion/<id_curso>/<tipo>/<id>')
def leccion(id_curso, tipo, id):
    if 'username' in session:
        session['section'] = 'leccion'
        id_rol = session['id_rol']

        # Determinar siguiente leccion
        siguiente = operaciones_sql.encontrar_siguiente(id_curso, id, tipo)
        print(siguiente)

        # Video
        if tipo == 'Video':
            video = operaciones_sql.get_video(id)
            print(video[1])
            return render_template('video.html', video=video, id_curso=id_curso, id_rol=id_rol, siguiente=siguiente)
        elif tipo == 'Cuestionario':
            cuestionario, preguntas_respuestas = operaciones_sql.get_cuestionario(id)
            return render_template('cuestionario.html', cuestionario=cuestionario, id_curso=id_curso, preguntas_respuestas=preguntas_respuestas, id_rol=id_rol, siguiente=siguiente)
        elif tipo == 'Lectura':
            lectura, paginas = operaciones_sql.get_lectura(id)
            print(paginas)
            return render_template('lectura.html', lectura=lectura, paginas=paginas, id_curso=id_curso, length=len(paginas), id_rol=id_rol, siguiente=siguiente)
        else:
            return redirect(url_for('cursos', id_rol=id_rol))
    else:
        return redirect(url_for('login', fail='False'))

@app.route('/subir_calificacion', methods=['POST'])
def subir_calificacion():
    # Recibir datos del formulario
    data = request.get_json()

    id_leccion = data['id']
    tipo = data['tipo']
    calificacion = data['calificacion']

    # Subir a la base de datos
    operaciones_sql.subir_calificacion(id_leccion, tipo, calificacion)

    return {"success": True}, 200


@app.route('/check', methods=['POST'])
def check():
    print(request.form)
    username_input = request.form['username']
    password_input = request.form['password']

    # Validar credenciales
    valid, id, name, id_rol = operaciones_sql.validate_credentials(username_input, password_input)

    if valid:
        #Guardamos los datos importantes que se necesitaran para otras partes de la pagina
        session['username'] = username_input
        session['id'] = id
        session['name'] = name
        session['id_rol'] = id_rol
        operaciones_sql.get_pfp(username_input)

        # Registrar entrada
        operaciones_sql.entrada(id)

        return redirect(url_for('homepage'))
    
    else:
        #Si no es valido redirige al login
        return redirect(url_for('login', fail='True'))

@app.route('/homepage', methods=['GET'])
def homepage():
    if 'username' in session:
        session['section'] = 'homepage'
        id_rol = session['id_rol']
        return render_template('homepage.html', id_rol=id_rol)
    else:
        return redirect(url_for('login', fail='False'))

@app.route('/login/<fail>', methods=['GET'])
def login(fail):
    if(fail == 'True'):
        return render_template('login.html', fail='True')
    else:
        return render_template('login.html', fail='False')
    
@app.route('/log_out')
def log_out():
    session.clear()
    return redirect(url_for('login', fail='False'))


@app.route('/Dar_de_alta', methods=["GET","POST"])
def alta():
    session['section'] = 'Alta'
    if 'username' in session:
        id_rol = session['id_rol']
        if id_rol == 2:
            if request.method == "POST":
                alumno = request.form['new_user']
                correo = request.form['new_mail']
                cel = request.form['phone_num']
                tipo_rol = request.form['rol_type']
                pswd = request.form['new_pswd']

                exists = operaciones_sql.verificar_estudiante(correo)

                print(exists)

                if not exists:
                    operaciones_sql.agregar_estudiantes(alumno, correo, cel, tipo_rol, pswd)
                    return render_template('dar_de_alta.html', saved = 'True', id_rol=id_rol)
                else:
                    return render_template('dar_de_alta.html', saved = 'False', id_rol=id_rol)
            else:
                return render_template('dar_de_alta.html', id_rol=id_rol)
        else:
            return redirect(url_for('cursos', id_rol=id_rol))
    else:
       return redirect(url_for('login', fail='False')) 

@app.route('/Alumnos')
def visualizar_alumnos():
    if 'username' in session:
        session['section'] = 'Vista_alumnos'
        id_rol = session['id_rol']
        if session['id_rol'] == 3 or session['id_rol'] == 2:
            alumnos = operaciones_sql.get_alumnos()
            return render_template('vista_usuarios.html', alumnos = alumnos, id_rol=id_rol)
        else:
            return redirect(url_for('cursos', id_rol=id_rol))
    else:
        return redirect(url_for('login', fail='False'))
    
@app.route('/Profesores')
def visualizar_profesores():
    if 'username' in session:
        session['section'] = 'Vista_profesores'
        id_rol = session['id_rol']
        if session['id_rol'] == 3 or session['id_rol'] == 2:
            profesores = operaciones_sql.get_profesores()
            return render_template('vista_usuarios.html', profesores = profesores, id_rol=id_rol)
        else:
            return redirect(url_for('cursos', id_rol=id_rol))
    else:
        return redirect(url_for('login', fail='False'))
    
    
@app.route('/')
def home():
    return redirect(url_for('login', fail='False'))


@app.route('/crear_curso_form', methods=['GET'])
def crear_curso_form():
    if 'username' in session:
        session['section'] = 'creacion_curso'
        id_rol = session['id_rol']
        if id_rol == 2:
            return render_template('CreacionCursos.html', id_rol=id_rol, curso=["", "", ""])
        else:
            return redirect(url_for('cursos', id_rol))
    else:
        return redirect(url_for('login', fail = "False"))
    
@app.route('/editar_curso_form/<id_curso>', methods=['GET'])
def editar_curso_form(id_curso):
    session['section'] = 'edicion_curso'
    id_rol = session['id_rol']
    if 'username' in session:
        if id_rol == 2:
            curso = operaciones_sql.get_curso_info(id_curso)
            return render_template('CreacionCursos.html', id_rol=id_rol, id_curso=id_curso, curso=curso)
        else:
            return redirect(url_for('cursos'))
    else:
        redirect(url_for('login', fail = "False"))

@app.route('/crear_modulo_form', methods=['GET'])
def crear_modulo_form():
    id_rol = session['id_rol']
    if 'username' in session:
        return render_template('CreacionModulos.html', id_rol=id_rol)
    else:
        redirect(url_for('login', fail = "False"))

@app.route('/editar_modulo_form/<id_curso>', methods=['GET'])
def editar_modulo_form(id_curso):
    session['section'] = 'edicion_modulo'
    id_rol = session['id_rol']
    if 'username' in session:
        if id_rol == 2:
            curso = operaciones_sql.get_curso_info(id_curso)
            return render_template('CreacionModulos.html', id_rol=id_rol, id_curso=id_curso, curso=curso)
        else:
            return redirect(url_for('cursos'))
    else:
        redirect(url_for('login', fail = "False"))

@app.route('/crear_cuestionario_form', methods=['GET'])
def crear_cuestionario_form():
    session['section'] = "crear_cuestionario"
    if 'username' in session:
        return render_template('CreacionCuestionarios.html', id_rol = session['id_rol'])
    else:
        redirect(url_for('login', fail = "False"))

UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/crear_curso', methods=['POST'])
def crear_curso():
    # if 'username' not in session:
    #     return jsonify({'message': 'No autorizado'}), 401

    data = request.get_json()
    print("JSON recibido:", data)

    courseNombre = data.get('courseNombre')
    courseDescripcion = data.get('courseDescripcion')
    courseImagen_url = data.get('courseImagen_url')
    modulos =data.get('modulos')

    # To decode the Base64 image file
    for i, modulo in enumerate(modulos):
        contenidos = modulo.get('contenidos', [])
        for j, contenido in enumerate(contenidos):
            lectura_list = contenido.get('lecturaTexto', [])

            for k, lectura in enumerate(lectura_list):
                base64_str = lectura.get('imgPagina')

                if base64_str:
                  
                    match = re.match(r'data:image/(?P<ext>[^;]+);base64,(?P<data>.+)', base64_str)
                    if match:
                        ext = match.group('ext')
                        img_data = base64.b64decode(match.group('data'))
                        filename = f'modulo{i+1}_contenido{j+1}_pagina{k+1}.{ext}'
                        filepath = os.path.join(UPLOAD_FOLDER, filename)

                        with open(filepath, 'wb') as f:
                            f.write(img_data)

                        lectura['imgPagina'] = filepath

                        print(f'✅ Imagen guardada: {filepath}')
                    else:
                        print(f'⚠️ Base64 inválido en modulo {i+1}, contenido {j+1}, página {k+1}')
                else:
                    print(f'⚠️ No se encontró imgPagina en página {k+1}')



    try:
        operaciones_sql.crear_curso(courseNombre, courseDescripcion, courseImagen_url, modulos)
        return jsonify({'message': 'Curso creado exitosamente'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al crear el curso'}), 500
    
@app.route('/editar_curso', methods=['POST'])
def editar_curso():
    # if 'username' not in session:
    #     return jsonify({'message': 'No autorizado'}), 401

    data = request.get_json()
    print("JSON recibido:", data)
    courseID = data.get('idCurso')
    courseNombre = data.get('courseNombre')
    courseDescripcion = data.get('courseDescripcion')
    courseImagen_url = data.get('courseImagen_url')
    modulos =data.get('modulos')

    # To decode the Base64 image file
    for i, modulo in enumerate(modulos):
        contenidos = modulo.get('contenidos', [])
        for j, contenido in enumerate(contenidos):
            lectura_list = contenido.get('lecturaTexto', [])

            for k, lectura in enumerate(lectura_list):
                base64_str = lectura.get('imgPagina')

                if base64_str:
                  
                    match = re.match(r'data:image/(?P<ext>[^;]+);base64,(?P<data>.+)', base64_str)
                    if match:
                        ext = match.group('ext')
                        img_data = base64.b64decode(match.group('data'))
                        filename = f'modulo{i+1}_contenido{j+1}_pagina{k+1}.{ext}'
                        filepath = os.path.join(UPLOAD_FOLDER, filename)

                        with open(filepath, 'wb') as f:
                            f.write(img_data)

                        lectura['imgPagina'] = filepath

                        print(f'✅ Imagen guardada: {filepath}')
                    else:
                        print(f'⚠️ Base64 inválido en modulo {i+1}, contenido {j+1}, página {k+1}')
                else:
                    print(f'⚠️ No se encontró imgPagina en página {k+1}')

    try:
        operaciones_sql.editar_curso(courseID, courseNombre, courseDescripcion, courseImagen_url, modulos)
        return jsonify({'message': 'Curso editado exitosamente'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al editar el curso'}), 500


@app.route('/asignar_alumno/<id_curso>/<id_alumno>')
def asignar_alumno(id_curso, id_alumno):
    if 'username' in session:
        operaciones_sql.asignar_alumno(id_curso, id_alumno)
        return redirect(url_for('vista_curso', id_curso=id_curso))
    else:
        return redirect(url_for('login', fail='False'))
    
@app.route('/desempeno')
def desempeno():
    session['section'] = 'desempeno'
    if 'username' in session:
        return render_template('desempeno.html', id_rol = session['id_rol'])
    else:
        return redirect(url_for('login', fail='False'))

@app.route('/remover_alumno/<id_curso>/<id_alumno>')
def remover_alumno(id_curso, id_alumno):
    if 'username' in session:
        operaciones_sql.remover_alumno(id_curso, id_alumno)
        return redirect(url_for('vista_curso', id_curso=id_curso))
    else:
        return redirect(url_for('login', fail='False'))

#edicion de alumnos
@app.route('/editar_alumno/<id_alumno>', methods = ['GET', 'POST'])
def editar_alumno(id_alumno):
    if 'username' in session:
        session['section'] = "editar_alumno"
        datos_originales = operaciones_sql.info_alumno(id_alumno)
        datos = operaciones_sql.info_alumno(id_alumno)
        if session['id_rol'] == 2:
            if request.method == "GET":
                if id_alumno:
                    datos = operaciones_sql.info_alumno(id_alumno)
                    return render_template('dar_de_alta.html', id_rol = session['id_rol'], id_alumno = id_alumno, datos = datos)
                else:
                    return redirect(url_for('Alta'))
            if request.method == "POST":
                nuevo_nombre = request.form['new_user']
                nuevo_correo = request.form['new_mail']
                nuevo_cel = request.form['phone_num']
                nuevo_rol = request.form['rol_type']
                nueva_pswd = request.form['new_pswd']

                operaciones_sql.modificar_alumno(id_alumno, nuevo_nombre, nuevo_correo, nuevo_cel, nuevo_rol, nueva_pswd)
                datos = operaciones_sql.info_alumno(id_alumno)
                
                if datos != datos_originales:
                    return render_template('dar_de_alta.html', updated = 'True', id_rol=session['id_rol'], id_alumno = id_alumno, datos = datos)
                else:
                    return render_template('dar_de_alta.html', updated = 'False', id_rol=session['id_rol'], id_alumno = id_alumno, datos = datos)
        else:
            return redirect(url_for('cursos', id_rol=session['id_rol']))
    else:
       return redirect(url_for('login', fail='False')) 

@app.route('/eliminar_alumnos/<id_alumno>/<id_rol>')
def eliminar_alumno(id_alumno,id_rol):
    session['section'] = 'eliminar_alumno'
    if 'username' in session:
        if session['id_rol'] == 2:
            operaciones_sql.eliminar_alumno(id_alumno)
            if id_rol == '1':
                return redirect(url_for('visualizar_alumnos'))
            else:
                return redirect(url_for('visualizar_profesores'))
        else:
            return redirect(url_for('cursos', id_rol=session['id_rol']))
    else:
        return redirect(url_for('login', fail='False'))

@app.route('/alumnos_todos/<id_curso>/<tipo>')
def alumnos_todos(id_curso, tipo):
    operaciones_sql.alumnos_todos(id_curso, tipo)
    return redirect(url_for('vista_curso', id_curso=id_curso))

@app.route('/eliminar_curso/<id_curso>', methods=['POST'])
def eliminar_curso(id_curso):
    operaciones_sql.eliminar_curso(id_curso)
    return redirect(url_for('cursos'))

@app.route('/api/obtener_curso/<int:id_curso>', methods=['GET'])
def obtener_curso(id_curso):
    data = operaciones_sql.get_curso_json(id_curso)
    return jsonify(data)

@app.route('/user_pfp/<id_alumno>')
def obtener_imagen(id_alumno):
    pfp = operaciones_sql.get_pfp_VA(id_alumno)
    if None not in pfp:
        return Response(pfp, mimetype="image/jpeg")
    else:
        with open('app/static/img/default_pfp.jpg', 'rb') as image:
            default_pfp = image.read()
        return Response(default_pfp, mimetype="image/jpeg")

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000)
