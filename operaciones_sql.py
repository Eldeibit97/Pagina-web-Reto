import mysql.connector
import datetime



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
        query = "SELECT u.ID_Usuario, u.Nom_Usuario FROM Usuarios u WHERE u.Correo_Cliente = '" + username + "'"
        cursor.execute(query)
        answer = cursor.fetchall()[0]

        user_id = answer[0]
        name = answer[1]

        cursor.close()
        connection.close()
        return True, user_id, name
    else:
        cursor.close()
        connection.close()
        return False, 0, "_"
    
def get_pfp(username):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT u.Img_Usuario FROM Usuarios u WHERE u.Correo_Cliente = '" + username + "'"
    cursor.execute(query)
    pfp = cursor.fetchall()

    cursor.close()
    connection.close()

    if pfp and pfp[0][0]:
        with open("static/images/pfp.jpg", "wb") as file:
            file.write(pfp[0][0])
        return "pfp.jpg"
    else:
        return None
    
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

# Obtener las lecciones de un curso
def get_lecciones(id_curso):
    connection = connect()
    cursor = connection.cursor()

    # Obtener modulos
    query = "SELECT * FROM Modulos m WHERE m.ID_Curso = " + str(id_curso)
    cursor.execute(query)
    modulos = cursor.fetchall()

    list = []

    for modulo in modulos:
        # obtener lecciones
        id_str = str(modulo[1])
        query = "SELECT l.ID_Lectura AS ID, 'Lectura' AS tipo, l.Fecha_Creacion AS fechaCreacion, l.Nom_Lectura AS nombre FROM Lectura l WHERE l.ID_Modulo = " + id_str + " UNION ALL SELECT v.ID_Video AS ID, 'Video' AS tipo, v.Fecha_Creacion AS fechaCreacion, v.Nombre_Video AS nombre FROM Video v WHERE v.ID_Modulo = " + id_str + " UNION ALL SELECT c.ID_Cuestionario AS ID, 'Cuestionario' AS tipo, c.Fecha_Creacion AS fechaCreacion, c.Nom_Cuestionario AS nombre FROM Cuestionario c WHERE c.ID_Modulo = " + id_str + " ORDER BY fechaCreacion;"
        cursor.execute(query)
        lecciones = cursor.fetchall()
        list.append([modulo, lecciones])

    cursor.close()
    connection.close()

    return list


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
