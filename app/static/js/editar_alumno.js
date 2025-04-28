window.onload = function () {
  seccion = document.getElementById("seccion").value

  if (seccion == "editar_alumno"){
    document.getElementById("text_name").innerText = "Nombre del estudiante que se modificara";
    document.getElementById("text_mail").innerText = "Nuevo correo que se le asignara";
    document.getElementById("text_cel").innerText = "Telefono del estudiante";
    document.getElementById("text_pswd").innerText = "Nueva contraseña que se le asignara";
    document.getElementById("new_user").value = document.getElementById("user_name").value;
    document.getElementById("new_mail").value = document.getElementById("user_mail").value;
    document.getElementById("phone_num").value = document.getElementById("user_cel").value;
    document.getElementById("new_rol").value = document.getElementById("user_rol").value;
    document.getElementById("new_pswd").value = document.getElementById("user_pswd").value;
  }
}