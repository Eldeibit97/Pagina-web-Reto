from flask import Flask, redirect, url_for, request, render_template, session
import operaciones_sql

app = Flask(__name__)
app.secret_key = 'super secret key'

## Funciones ##





# Endpoints

@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    if request.method == 'GET':
        if 'username' in session:
            
            cursos = operaciones_sql.find_cursos(session['username'])
            return render_template('cursos.html', cursos=cursos)
        
        else:
            return redirect(url_for('login', fail='False'))
    else:
        curso_nombre = request.form['curso_id']
        print(curso_nombre)
        return render_template('vista_curso.html', curso_nombre=curso_nombre)


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


if __name__ == '__main__':
    app.run(debug=True)
