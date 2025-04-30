document.addEventListener("DOMContentLoaded", function () {
    const addQuestionButton = document.getElementById("addQuestion");
    const questionList = document.getElementById("questionList");

    questionList.addEventListener("click", function (event) {
        if (event.target && event.target.classList.contains("deletePreguntaButton")) {
            const questionFieldset = event.target.closest(".question");
            if (questionFieldset) {
                questionFieldset.remove();
                renumberQuestions();
            }
        }
    });



addQuestionButton.addEventListener("click", function () {
    const newQuestion = document.createElement("fieldset");
    newQuestion.classList.add("question");

    const legend = document.createElement("legend");
    legend.classList.add('legend')
    newQuestion.appendChild(legend);

    const deleteBtn = document.createElement("button");
    deleteBtn.innerHTML = "x";
    deleteBtn.classList.add("deletePreguntaButton");
    newQuestion.appendChild(deleteBtn);

    const questionInput = document.createElement("input");
    questionInput.type = "text";
    questionInput.classList.add("inputstyle")
    questionInput.placeholder = "Ingresar Pregunta";
    newQuestion.appendChild(questionInput);

    const optionsContainer = document.createElement("div");
    optionsContainer.classList.add("options");

    for (let i = 1; i <= 4; i++) {
        const optionWrapper = document.createElement("div");
        optionWrapper.classList.add("option-wrapper");

        const optionInput = document.createElement("input");
        optionInput.type = "text";
        optionInput.classList.add('inputstyle')
        optionInput.placeholder = `Opcion ${i}`;
        optionWrapper.appendChild(optionInput);

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.title = "Esta es la respuesta correcta";
        optionWrapper.appendChild(checkbox);

        const label = document.createElement("label");
        label.classList.add("incorrect-option");
        label.textContent = "Incorrecta";
        optionWrapper.appendChild(label);

        checkbox.addEventListener("change", function() {
            if (checkbox.checked) {
                label.classList.remove("incorrect-option");
                label.classList.add("correct-option");
                label.textContent = "Correcta";
            } else {
                label.classList.remove("correct-option");
                label.classList.add("incorrect-option");
                label.textContent = "Incorrecta";
            }
        });

        optionsContainer.appendChild(optionWrapper);
    }

    newQuestion.appendChild(optionsContainer);

    questionList.insertBefore(newQuestion, addQuestionButton);
    

    renumberQuestions();
});

document.querySelectorAll(".option-wrapper input[type='checkbox']").forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        const label = this.nextElementSibling;
        if (this.checked) {
            label.classList.remove("incorrect-option");
            label.classList.add("correct-option");
            label.textContent = "Correcta";
        } else {
            label.classList.remove("correct-option");
            label.classList.add("incorrect-option");
            label.textContent = "Incorrecta";
        }
    });
});


function renumberQuestions() {
    const allQuestions = document.querySelectorAll(".question");
    allQuestions.forEach((questionElem, index) => {
        const legend = questionElem.querySelector("legend");
        if (legend) {
            legend.textContent = "Pregunta " + (index + 1);
        }
    });
}

renumberQuestions();
});

const cuestionarioTitle = sessionStorage.getItem('cuestionarioTitle')  || "Nuevo Cuestionario";

document.addEventListener("DOMContentLoaded", function () {

document.getElementById("Title").textContent = "Editar Cuestionario: " + cuestionarioTitle;

const saveButton = document.getElementById("saveButton");

saveButton.addEventListener("click", function () {
    const questions = document.querySelectorAll(".question");
    let questionData = [];

    questions.forEach((question, index) => {
        let pregunta = question.querySelector("input[type='text']").value;
        let opciones = [];
        let correctas = [];

        question.querySelectorAll(".option-wrapper").forEach((optionWrapper, optionIndex) => {
            let opcionTexto = optionWrapper.querySelector("input[type='text']").value;
            let checkbox = optionWrapper.querySelector("input[type='checkbox']");

            opciones.push(opcionTexto);
            correctas.push(checkbox.checked ? 1 : 0); 

        });

        questionData.push({
            id: index + 1,
            pregunta: pregunta,
            opciones: opciones,
            correctas: correctas
        });
    });

    
    const jsonData = JSON.stringify({
        title: cuestionarioTitle,
        preguntas: questionData
    });
    console.log(jsonData);
    
    sessionStorage.setItem("cuestionarioData", jsonData);

    alert("Saved");

    window.location.href = "/crear_modulo_form";


});
});