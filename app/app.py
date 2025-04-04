from flask import Flask, jsonify, redirect, url_for, request, render_template, session
import operaciones_sql
#from openai import OpenAI
import os
import re
import ast

app = Flask(__name__)
app.secret_key = 'super secret key'



## Funciones ##


# Endpoints

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
        
        session['section'] = 'vista_curso'
        id_curso = request.form['id_curso']
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
    

@app.route('/vista_curso/<id_curso>')
def vista_curso(id_curso):
    return f'''
        <html>
        <head>
            <title>Redirecting...</title>
            <script type="text/javascript">
                window.onload = function() {{
                    document.getElementById('redirectForm').submit();
                }}
            </script>
        </head>
        <body>
            <form id="redirectForm" action="/cursos" method="POST">
                <input type="hidden" name="id_curso" value="{id_curso}">
            </form>
            
        </body>
        </html>
        '''

#vista de las lecciones
@app.route('/leccion/<id_curso>/<tipo>/<id>')
def leccion(id_curso, tipo, id):
    if 'username' in session:
        session['section'] = 'leccion'
        id_rol = session['id_rol']
        # Video
        if tipo == 'Video':
            video = operaciones_sql.get_video(id)
            print(video[1])
            return render_template('video.html', video=video, id_curso=id_curso, id_rol=id_rol)
        elif tipo == 'Cuestionario':
            cuestionario, preguntas_respuestas = operaciones_sql.get_cuestionario(id)
            return render_template('cuestionario.html', cuestionario=cuestionario, id_curso=id_curso, preguntas_respuestas=preguntas_respuestas, id_rol=id_rol)
        elif tipo == 'Lectura':
            lectura, paginas = operaciones_sql.get_lectura(id)
            print(paginas)
            return render_template('lectura.html', lectura=lectura, paginas=paginas, id_curso=id_curso, length=len(paginas), id_rol=id_rol)
        else:
            return redirect(url_for('cursos', id_rol=id_rol))
    else:
        return redirect(url_for('login', fail='False'))



@app.route('/whirlChat', methods=['GET', 'POST'])
def whirlChat():
    # Initialize history only if it doesn't exist yet
    if 'history' not in session:
        session['history'] = [
            {"role": "system", "content": "¡Hola! Soy WhirlChat, tu asistente personal de aprendizaje en Whirlpool. ¿En qué puedo ayudarte hoy?"}
        ]
        session.modified = True  # Mark session as modified
    
    if request.method == 'GET':
        if 'username' in session:
            session['section'] = 'whirlChat'
            return render_template('whirlChat.html', history=session['history'])
        else:
            return redirect(url_for('login', fail='False'))
    else:
        # Make a copy of the current history
        history = session.get('history', []).copy()
        user_msg = request.form["message"]
        
        # Add the user message
        history.append({"role": "user", "content": user_msg})

        try:
            response = OpenAI(
                base_url="http://127.0.0.1:1234/v1",
                api_key="lm-studio"
            )
            MODEL = "qwen2.5-7b-instruct-1m"

            completion = response.chat.completions.create(
                model=MODEL,
                messages=history,
            )

            ai_response = completion.choices[0].message.content
            ai_response = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL)
            history.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            ai_response = f"Ocurrió un error: {str(e)}"
            history.append({"role": "assistant", "content": ai_response})
        
        # Update the session with the new history
        session['history'] = history
        session.modified = True  # Mark session as modified
        
        return render_template("whirlChat.html", history=history)

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
        session['username'] = username_input
        session['id'] = id
        session['name'] = name
        session['id_rol'] = id_rol
        print(id)
        operaciones_sql.get_pfp(username_input)

        return redirect(url_for('cursos', id_rol=id_rol))
    
    else:
        return redirect(url_for('login', fail='True', id_rol=id_rol))


@app.route('/login/<fail>', methods=['GET'])
def login(fail):
    if(fail == 'True'):
        return render_template('login.html', fail='True')
    else:
        return render_template('login.html', fail='False')


@app.route('/Dar_de_alta', methods=["GET","POST"])
def alta():
    session['section'] = 'Alta'
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

@app.route('/Alumnos')
def visualizar_alumnos():
    session['section'] = 'Vista_alumnos'
    id_rol = session['id_rol']
    if session['id_rol'] == 3:
        alumnos = operaciones_sql.get_alumnos()
        return render_template('vista_alumnos.html', alumnos = alumnos, id_rol=id_rol)
    else:
        return redirect(url_for('cursos', id_rol=id_rol))
    
    
@app.route('/')
def home():
    return redirect(url_for('login', fail='False'))


@app.route('/crear_curso_form', methods=['GET'])
def crear_curso_form():
    session['section'] = 'creacion_curso'
    id_rol = session['id_rol']
    if session['id_rol'] == 2:
        return render_template('CreacionCursos.html', id_rol=id_rol)
    else:
        return redirect(url_for('cursos', id_rol))

@app.route('/crear_modulo_form', methods=['GET'])
def crear_modulo_form():
    id_rol = session['id_rol']
    return render_template('CreacionModulos.html', id_rol=id_rol)


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


    try:
        operaciones_sql.crear_curso(courseNombre, courseDescripcion, courseImagen_url, modulos)
        return jsonify({'message': 'Curso creado exitosamente'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al crear el curso'}), 500


@app.route('/asignar_alumno/<id_curso>/<id_alumno>')
def asignar_alumno(id_curso, id_alumno):
    if 'username' in session:
        operaciones_sql.asignar_alumno(id_curso, id_alumno)
        return redirect(url_for('vista_curso', id_curso=id_curso))
    else:
        return redirect(url_for('login', fail='False'))

@app.route('/remover_alumno/<id_curso>/<id_alumno>')
def remover_alumno(id_curso, id_alumno):
    if 'username' in session:
        operaciones_sql.remover_alumno(id_curso, id_alumno)
        return redirect(url_for('vista_curso', id_curso=id_curso))
    else:
        return redirect(url_for('login', fail='False'))

@app.route('/alumnos_todos/<id_curso>/<tipo>')
def alumnos_todos(id_curso, tipo):
    operaciones_sql.alumnos_todos(id_curso, tipo)
    return redirect(url_for('vista_curso', id_curso=id_curso))


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
