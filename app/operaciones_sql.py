import mysql.connector
import datetime
import os
from flask import session


# Conectarse a base de datos
def connect():
    connection = mysql.connector.connect(
        host='mysql-2ba70603-tec-18f1.d.aivencloud.com',
        port=18986,
        user='avnadmin',
        password='AVNS_Pw5Y7FYmuibFg8VaXaQ',
        database='SoluTec',
        ssl_ca='certificado.pem',
    )

    return connection

# Validar credenciales
def validate_credentials(username, password):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT CASE WHEN COUNT(*) > 0 THEN TRUE ELSE FALSE END AS is_valid FROM Usuarios u WHERE u.Correo_Cliente = '" + username + "' AND u.Password = '" + password + "'"
    cursor.execute(query)
    is_valid = cursor.fetchall()

    if is_valid[0][0] == 1:
        query = "SELECT u.ID_Usuario, u.Nom_Usuario, u.ID_Rol FROM Usuarios u WHERE u.Correo_Cliente = '" + username + "'"
        cursor.execute(query)
        answer = cursor.fetchall()[0]

        user_id = answer[0]
        name = answer[1]
        rol = answer[2]

        cursor.close()
        connection.close()
        return True, user_id, name, rol
    else:
        cursor.close()
        connection.close()
        return False, 0, "_",0
    
def get_pfp(username):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT u.Img_Usuario FROM Usuarios u WHERE u.Correo_Cliente = '" + username + "'"
    cursor.execute(query)
    pfp = cursor.fetchall()

    cursor.close()
    connection.close()

    if pfp and pfp[0][0]:
        os.makedirs("static/images", exist_ok=True)
        with open("static/images/pfp.jpg", "wb") as file:
            file.write(pfp[0][0])
        return "pfp.jpg"
    else:
        return None
    
#Dar de alta a nuevos tecnicos estudiantes/profesores
def agregar_estudiantes(nombre, correo, telefono, rol_id, pswd):
    connection = connect()
    cursor = connection.cursor()

    query = "INSERT INTO Usuarios(Nom_Usuario, Correo_Cliente, Tel_Cliente, Password, ID_Rol) VALUES('" + nombre + "', '" + correo + "', " + str(telefono) + ", '" + pswd + "', " + str(rol_id) + ")"
    cursor.execute(query)
    
    connection.commit()
    cursor.close()
    connection.close()

#Verificar que el usuario que se intente crear no exista ya o 
# las credenciales planteadas ya pertenezcan a otro tecnico
def verificar_estudiante(correo):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT CASE WHEN COUNT(*) = 1 THEN TRUE ELSE FALSE END AS 'already exists' FROM Usuarios u WHERE Correo_Cliente = '"+ correo +"'"
    cursor.execute(query)
    exists = cursor.fetchall()

    cursor.close()
    connection.close()

    if exists[0][0] == 1:
        return True
    else:
        return False


# Encontrar cursos del usuario (tecnico)
def find_cursos(id):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT uc.ID_Curso, c.Nom_Curso, c.Descripcion, c.Link_Img_Curso FROM Usuario_Curso uc LEFT JOIN Cursos c ON uc.ID_Curso = c.ID_Curso WHERE uc.ID_Usuario = " + str(id)
    cursor.execute(query)
    cursos = cursor.fetchall()

    cursor.close()
    connection.close()

    return cursos

# Obtener todos los cursos creados (Para el admin y el profesor)
def get_cursos():
    connection = connect()
    cursor = connection.cursor()

    query = 'SELECT ID_Curso, Nom_Curso, Descripcion, Link_Img_Curso  FROM Cursos c'
    cursor.execute(query)
    cursos = cursor.fetchall()

    cursor.close()
    connection.close()

    return cursos

# Obtener a los diferentes alumnos ya registrados en la DB
def get_alumnos():
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT u.Nom_Usuario, u.Img_Usuario FROM Usuarios u WHERE u.ID_Rol = 1"
    cursor.execute(query)
    alumnos = cursor.fetchall()

    cursor.close()
    connection.close()

    return alumnos

# Obtener las lecciones de un curso
def get_lecciones(id_curso):
    connection = connect()
    cursor = connection.cursor()

    # Obtener modulos
    query = "SELECT * FROM Modulos m WHERE m.ID_Curso = " + str(id_curso)
    cursor.execute(query)
    modulos = cursor.fetchall()

    list = []
    completadas = 0.0
    total = 0.0
    for modulo in modulos:
        # obtener lecciones
        id_str = str(modulo[1])
        query = "SELECT l.ID_Lectura AS ID, 'Lectura' AS tipo, l.Fecha_Creacion AS fechaCreacion, l.Nom_Lectura AS nombre FROM Lectura l WHERE l.ID_Modulo = " + id_str + " UNION ALL SELECT v.ID_Video AS ID, 'Video' AS tipo, v.Fecha_Creacion AS fechaCreacion, v.Nombre_Video AS nombre FROM Video v WHERE v.ID_Modulo = " + id_str + " UNION ALL SELECT c.ID_Cuestionario AS ID, 'Cuestionario' AS tipo, c.Fecha_Creacion AS fechaCreacion, c.Nom_Cuestionario AS nombre FROM Cuestionario c WHERE c.ID_Modulo = " + id_str + " ORDER BY fechaCreacion;"
        cursor.execute(query)
        lecciones = cursor.fetchall()

        
        
        # obtener calificaciones de las lecciones
        lecciones_lista = []

        for leccion in lecciones:
            if leccion[1] == 'Lectura':
                query = "SELECT IF((SELECT COUNT(*) FROM Usuario_Lectura ul WHERE ID_Lectura = " + str(leccion[0]) + " AND ID_Usuario = " + str(session['id']) +  " AND Fecha_Fin IS NOT NULL) > 0, 100, -1)"
                cursor.execute(query)
            elif leccion[1] == 'Video':
                query = "SELECT IF((SELECT COUNT(*) FROM Usuario_Video uv  WHERE ID_Video  = " + str(leccion[0]) + " AND ID_Usuario = " + str(session['id']) +  " AND Fecha_Fin IS NOT NULL) > 0, 100, -1)"
                cursor.execute(query)
            elif leccion[1] == 'Cuestionario':
                query = "SELECT IFNULL((SELECT Puntaje FROM Evaluaciones WHERE ID_Usuario = " + str(session['id']) +  " AND ID_Cuestionario = " + str(leccion[0]) + " ORDER BY Fecha_Fin DESC LIMIT 1), -1)"
                cursor.execute(query)
            
            calificacion = cursor.fetchone()
            lecciones_lista.append([leccion, calificacion[0]])

            if calificacion[0] != -1 :
                completadas = completadas + calificacion[0]/100
            total = total + 1


        list.append([modulo, lecciones_lista])

    cursor.close()
    connection.close()

    # calcular progreso
    if total == 0:
        progreso = 0
    else:
        progreso = completadas / total * 100
    progreso = round(progreso, 2)

    return list, progreso

# Crear y agregar cursos 
def crear_curso(nom_curso, desc_curso, img_curso, Modulos): 
    connection = connect()
    cursor = connection.cursor()

    query_curso = "INSERT INTO Cursos (Nom_Curso, Descripcion, Link_Img_Curso) VALUES (%s, %s, %s);"
    values_curso = (nom_curso, desc_curso, img_curso)
    cursor.execute(query_curso, values_curso)

    curso_id = cursor.lastrowid

    query_modulo = "INSERT INTO Modulos (Nom_Modulo, ID_Curso) VALUES (%s, %s);"
    query_lectura = "INSERT INTO Lectura (Nom_Lectura, ID_Modulo, Fecha_Creacion) VALUES (%s, %s, %s);"
    query_video = "INSERT INTO Video (Nombre_Video, Link_Video, ID_Modulo, Fecha_Creacion) VALUES (%s, %s, %s, %s);"
    query_cuestionario = "INSERT INTO Cuestionario (Nom_Cuestionario, ID_Modulo, Fecha_Creacion) VALUES (%s, %s, %s);"

    for modulo in Modulos:
        nom_modulo = modulo['nomModulo']
        values_modulo = (nom_modulo, curso_id)
        cursor.execute(query_modulo, values_modulo)

        modulo_id = cursor.lastrowid
        fecha_creacion = datetime.datetime.now()

        for tarjeta in modulo['tarjetas']:
            tipo_archivo = tarjeta['tipoArchivo']
            nom_tarjeta = tarjeta['nomTarjeta']

            if tipo_archivo == 'lectura':
                # lectura_text = tarjeta.get('lecturaText', '')
                values_lectura = (nom_tarjeta, modulo_id, fecha_creacion)
                cursor.execute(query_lectura, values_lectura)

            elif tipo_archivo == 'video':
                video_url = tarjeta.get('videoUrl', '')
                values_video = (nom_tarjeta, video_url, modulo_id, fecha_creacion)
                cursor.execute(query_video, values_video)

            elif tipo_archivo == 'cuestionario':
                # pregunta = tarjeta.get('pregunta', '')
                values_cuestionario = (nom_tarjeta, modulo_id, fecha_creacion)
                cursor.execute(query_cuestionario, values_cuestionario)

    connection.commit() #commit the change

    cursor.close()
    connection.close()    
#
def get_curso(id):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT c.Nom_Curso, c.Descripcion FROM Cursos c WHERE c.ID_Curso = " + str(id)
    cursor.execute(query)
    curso = cursor.fetchall()
    curso = curso[0]

    cursor.close()
    connection.close()
    return curso


## Video ##
def get_video(id):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT v.Nombre_Video, v.Link_Video, v.ID_Video FROM Video v WHERE v.ID_Video = " + str(id)
    cursor.execute(query)
    video = cursor.fetchall()
    video = video[0]

    # Registrar inicio
    query = "INSERT INTO Usuario_Video (Fecha_Inicio, ID_Usuario, ID_Video) VALUES (NOW(), " + str(session['id']) + ", " + str(id) + ")"
    cursor.execute(query)
    connection.commit()


    cursor.close()
    connection.close()
    return video


## Cuestionario ##
def get_cuestionario(id):
    connection = connect()
    cursor = connection.cursor()

    # Obtener el nombre y tiempo del cuestionario
    query = "SELECT c.Nom_Cuestionario, c.Tiempo, c.ID_Cuestionario FROM Cuestionario c WHERE c.ID_Cuestionario = " + str(id)
    cursor.execute(query)
    cuestionario = cursor.fetchall()
    cuestionario = cuestionario[0]

    # Obtener preguntas y respuestas
    query = "SELECT p.Pregunta, p.ID_Pregunta FROM Preguntas p WHERE p.ID_Cuestionario = " + str(id)
    cursor.execute(query)
    preguntas = cursor.fetchall()
    preguntas_respuestas = []

    # Obtener respuestas
    for pregunta in preguntas:
        query = "SELECT * FROM Respuestas r WHERE r.ID_Pregunta = " + str(pregunta[1])
        cursor.execute(query)
        respuestas = cursor.fetchall()
        preguntas_respuestas.append([pregunta, respuestas])

    #print(preguntas_respuestas)

    # Registrar inicio
    query = "INSERT INTO Evaluaciones (ID_Usuario, ID_Cuestionario, Fecha_Inicio ) VALUES (" + str(session['id']) + ", " + str(id) + ", NOW())"
    cursor.execute(query)
    connection.commit()

    cursor.close()
    connection.close()
    return cuestionario, preguntas_respuestas


## Lectura ##
def get_lectura(id):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT * FROM Lectura l WHERE l.ID_Lectura = " + str(id)
    cursor.execute(query)
    lectura = cursor.fetchall()
    lectura = lectura[0]

    # obtener las paginas
    query = "SELECT p.ID_Pagina, p.Texto_Pagina, i.URL_Imagen, p.Nom_Pagina FROM Pagina p LEFT JOIN Imagen i ON p.ID_Pagina = i.ID_Pagina WHERE p.ID_Lectura = " + str(id) + " ORDER BY p.ID_Pagina ASC"
    cursor.execute(query)
    paginas = cursor.fetchall()

    # Registrar inicio
    query = "INSERT INTO Usuario_Lectura (Fecha_Inicio, ID_Usuario, ID_Lectura) VALUES (NOW(), " + str(session['id']) + ", " + str(id) + ")"
    cursor.execute(query)
    connection.commit()

    cursor.close()
    connection.close()
    return lectura, paginas



## Subir calificacion ##
def subir_calificacion(id_leccion, tipo, calificacion):
    connection = connect()
    cursor = connection.cursor()

    if tipo == 'Video':
        query = "UPDATE Usuario_Video SET Fecha_Fin = NOW() WHERE ID_Usuario = " + str(session['id']) + " AND ID_Video = " + str(id_leccion) + " ORDER BY Fecha_Inicio DESC LIMIT 1"
        cursor.execute(query)
        connection.commit()
    elif tipo == "Lectura":
        query = "UPDATE Usuario_Lectura SET Fecha_Fin = NOW() WHERE ID_Usuario = " + str(session['id']) + " AND ID_Lectura = " + str(id_leccion) + " ORDER BY Fecha_Inicio DESC LIMIT 1"
        cursor.execute(query)
        connection.commit()
    elif tipo == "Cuestionario":
        query = "UPDATE Evaluaciones SET Fecha_Fin = NOW(), Puntaje = " + str(calificacion) + " WHERE ID_Usuario = " + str(session['id']) + " AND ID_Cuestionario = " + str(id_leccion) + " ORDER BY Fecha_Inicio DESC LIMIT 1"
        cursor.execute(query)
        connection.commit()

def get_alumnos_curso(id_curso):
    connection = connect()
    cursor = connection.cursor()

    query = """
        SELECT u.Nom_Usuario, u.ID_Usuario FROM Usuarios u
        LEFT JOIN Usuario_Curso uc ON uc.ID_Usuario = u.ID_Usuario
        WHERE ID_Rol = 1 AND uc.ID_Curso = """ + str(id_curso)
    cursor.execute(query)
    asignados = cursor.fetchall()

    query = """
        SELECT u.Nom_Usuario, u.ID_Usuario
        FROM Usuarios u
        WHERE u.ID_Rol = 1
        AND u.ID_Usuario NOT IN (
            SELECT uc.ID_Usuario
            FROM Usuario_Curso uc
            WHERE uc.ID_Curso = """ + str(id_curso) + ")"
    cursor.execute(query)
    no_asignados = cursor.fetchall()

    cursor.close()
    connection.close()

    return asignados, no_asignados

def asignar_alumno(id_curso, id_usuario):
    connection = connect()
    cursor = connection.cursor()

    query = "INSERT INTO Usuario_Curso (ID_Usuario, ID_Curso) VALUES (" + str(id_usuario) + ", " + str(id_curso) + ")"
    cursor.execute(query)
    connection.commit()

    cursor.close()
    connection.close()

def remover_alumno(id_curso, id_usuario):
    connection = connect()
    cursor = connection.cursor()

    query = "DELETE FROM Usuario_Curso WHERE ID_Usuario = " + str(id_usuario) + " AND ID_Curso = " + str(id_curso)
    cursor.execute(query)
    connection.commit()

    cursor.close()
    connection.close()


## Asignar/Remover todos los alumnos de un curso
def alumnos_todos(id_curso, tipo):
    connection = connect()
    cursor = connection.cursor()

    if tipo == 'asignar':
        query = """
        INSERT INTO Usuario_Curso (ID_Usuario, ID_Curso)
        SELECT u.ID_Usuario, %s
        FROM Usuarios u
        WHERE u.ID_Rol = 1
        AND u.ID_Usuario NOT IN (
        SELECT uc.ID_Usuario
        FROM Usuario_Curso uc
        WHERE uc.ID_Curso = %s
        )
        """
        values = (id_curso, id_curso)
        cursor.execute(query, values)
        connection.commit()
    
    elif tipo == 'remover':
        query = """
            DELETE uc
            FROM Usuario_Curso uc
            JOIN Usuarios u ON uc.ID_Usuario = u.ID_Usuario
            WHERE uc.ID_Curso = %s AND u.ID_Rol = 1
        """
        values = (id_curso,)
        cursor.execute(query, values)
        connection.commit()
    cursor.close()
    connection.close()

def entrada(id):
    connection = connect()
    cursor = connection.cursor()

    # Verificar que no ha entrado el usuario en el dia actual
    query = """
        INSERT INTO Entrada (Fecha, ID_Usuario)
        SELECT CURDATE(), %s
        FROM DUAL
        WHERE NOT EXISTS (
            SELECT 1 FROM Entrada WHERE Fecha = CURDATE() AND ID_Usuario = %s
        );
    """
    values = (id, id)
    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()
