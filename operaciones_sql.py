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

    query = "SELECT uc.ID_Curso, c.Nom_Curso FROM Usuario_Curso uc LEFT JOIN Cursos c ON uc.ID_Curso = c.ID_Curso WHERE uc.ID_Usuario = 2"
    cursor.execute(query)
    cursos = cursor.fetchall()

    cursor.close()
    connection.close()

    return cursos
