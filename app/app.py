
from flask import Flask, redirect, jsonify, url_for, request, render_template, session
import operaciones_sql
from openai import OpenAI
import os
import re
import ast

app = Flask(__name__)
app.secret_key = 'super secret key'



## Funciones ##





# Endpoints

@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    if request.method == 'GET':
        if 'username' in session:
            session['section'] = 'cursos'
            cursos = operaciones_sql.find_cursos(session['id'])

            return render_template('cursos.html', cursos=cursos)
        
        else:
            return redirect(url_for('login', fail='False'))
    else:

        session['section'] = 'vista_curso'
        id_curso = request.form['id_curso']
        curso = operaciones_sql.get_curso(id_curso)
        nombre_curso = curso[0]
        descripcion_curso = curso[1]

        modulos = operaciones_sql.get_lecciones(id_curso)
        print(modulos)

        return render_template('vista_curso.html', id_curso=id_curso, nombre_curso=nombre_curso, descripcion_curso=descripcion_curso, modulos=modulos)
    
@app.route('/leccion/<id_curso>/<tipo>/<id>')
def leccion(id_curso, tipo, id):
    if 'username' in session:
        session['section'] = 'leccion'
        
        # Video
        if tipo == 'Video':
            video = operaciones_sql.get_video(id)
            print(video[1])
            return render_template('video.html', video=video, id_curso=id_curso)
        elif tipo == 'Cuestionario':
            cuestionario, preguntas_respuestas = operaciones_sql.get_cuestionario(id)
            return render_template('cuestionario.html', cuestionario=cuestionario, id_curso=id_curso, preguntas_respuestas=preguntas_respuestas)
        elif tipo == 'Lectura':
            lectura, paginas = operaciones_sql.get_lectura(id)
            print(paginas)
            return render_template('lectura.html', lectura=lectura, paginas=paginas, id_curso=id_curso, length=len(paginas))
        else:
            return redirect(url_for('cursos'))
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


@app.route('/check', methods=['POST'])
def check():
    print(request.form)
    username_input = request.form['username']
    password_input = request.form['password']

    # Validar credenciales
    valid, id, name = operaciones_sql.validate_credentials(username_input, password_input)

    if valid:
        session['username'] = username_input
        session['id'] = id
        session['name'] = name
        print(id)
        operaciones_sql.get_pfp(username_input)

        return redirect(url_for('cursos'))
    
    else:
        return redirect(url_for('login', fail='True'))


@app.route('/login/<fail>', methods=['GET'])
def login(fail):
    if(fail == 'True'):
        return render_template('login.html', fail='True')
    else:
        return render_template('login.html', fail='False')

    
@app.route('/')
def home():
    return redirect(url_for('login', fail='False'))


@app.route('/crear_curso_form', methods=['GET'])
def crear_curso_form():
    return render_template('CreacionCursos.html')

@app.route('/crear_modulo_form', methods=['GET'])
def crear_modulo_form():
    return render_template('CreacionModulos.html')

@app.route('/crear_cuestionario_form', methods=['GET'])
def crear_cuestionario_form():
    return render_template('CreacionCuestionarios.html')


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

if __name__ == '__main__':
    app.run(debug=True)
