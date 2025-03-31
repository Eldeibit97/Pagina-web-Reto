import mysql.connector



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
    
#Dar de alta a nuevos tecnicos estudiantes
def agregar_estudiantes(nombre, correo, telefono, pswd):
    connection = connect()
    cursor = connection.cursor()

    query = "INSERT INTO Usuarios(Nom_Usuario, Correo_Cliente, Tel_Cliente, Password, ID_Rol) VALUES ('"+ nombre +"', '"+ correo +"', "+ telefono +", '"+ pswd +"', '"+ 1 +"')"
    cursor.execute(query)
    
    cursor.close()
    connection.close()

"""def verificar_estudiante(correo):
    connection = connect()
    cursor = connection.cursor()

    query = "SELECT CASE WHEN COUNT(*) = 1 THEN TRUE ELSE FALSE END AS created FROM Usuarios u WHERE u.Correo_Cliente = 'A00232453@Tec.mx'"
    cursor.execute(query)
    created = cursor.fetchall()

    cursor.close()
    connection.close()

    return created[0][0]
"""

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

    
    
