/* ===============================
   CONFIG
================================ */
const RAG_GENERATE_URL = "/api/rag/generate-answer";


/* ===============================
   CSRF TOKEN
================================ */
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}


/* ===============================
   LOAD EXISTING QUESTIONS
================================ */
function getExistingQuestions() {
    const el = document.getElementById("questions-data");
    return el ? JSON.parse(el.textContent) : [];
}


/* ===============================
   AI AUTO FILL USING RAG
================================ */
async function generateWithAI(questionTextarea) {

    const card = questionTextarea.closest(".question-card");
    const expectedBox = card.querySelector(".expected");
    const keywordsBox = card.querySelector(".keywords");

    const question = questionTextarea.value.trim();

    if (!question) {
        alert("Please enter a question first");
        return;
    }

    expectedBox.value = "Generating using AI...";
    keywordsBox.value = "Generating...";

    try {
        const response = await fetch(RAG_GENERATE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: question })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        expectedBox.value = data.expected_solution || "";
        keywordsBox.value = (data.keywords || []).join(",");

    } catch (error) {
        console.error(error);
        expectedBox.value = "";
        keywordsBox.value = "";
        alert("AI generation failed ❌");
    }
}


/* ===============================
   ADD QUESTION UI
================================ */
function addQuestion(q = {}) {

    const container = document.getElementById("questionsContainer");

    container.insertAdjacentHTML("beforeend", `
        <div class="card p-3 mt-3 question-card">

            <label class="fw-semibold">Problem Statement</label>
            <textarea class="form-control mb-2 question"
                      rows="2"
                      onblur="generateWithAI(this)"
            >${q.question_text || ""}</textarea>

            <label class="fw-semibold">Expected Solution (Logic)</label>
            <textarea class="form-control mb-2 expected"
                      rows="2">${q.expected_solution || ""}</textarea>

            <label class="fw-semibold">Keywords (comma separated)</label>
            <input class="form-control mb-2 keywords"
                   value="${(q.keywords || []).join(",")}">

            <label class="fw-semibold">Allowed Languages</label>
            <input class="form-control mb-2 languages"
                   placeholder="c,cpp,java,python"
                   value="${(q.allowed_languages || []).join(",")}">

            <label class="fw-semibold">Max Marks</label>
            <input type="number"
                   class="form-control marks"
                   value="${q.max_marks || 10}">

        </div>
    `);
}


/* ===============================
   RENDER EXISTING QUESTIONS
================================ */
document.addEventListener("DOMContentLoaded", () => {
    const questions = getExistingQuestions();
    questions.forEach(q => addQuestion(q));
});


/* ===============================
   COLLECT QUESTIONS
================================ */
function collectQuestions() {

    const questions = [];

    document.querySelectorAll(".question-card").forEach(card => {

        questions.push({
            question_text: card.querySelector(".question").value.trim(),
            expected_solution: card.querySelector(".expected").value.trim(),

            keywords: card.querySelector(".keywords").value
                .split(",")
                .map(k => k.trim())
                .filter(Boolean),

            allowed_languages: card.querySelector(".languages").value
                .split(",")
                .map(l => l.trim().toLowerCase())
                .filter(Boolean),

            max_marks: parseInt(card.querySelector(".marks").value || 10)
        });

    });

    return questions;
}


/* ===============================
   SAVE ASSIGNMENT
================================ */
function saveAssignment() {

    const formData = new FormData();
    formData.append("title", assignmentTitle.value.trim());
    formData.append("description", assignmentDescription.value.trim());
    formData.append("max_marks", assignmentMarks.value);

    fetch(SAVE_ASSIGNMENT_URL, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        body: formData
    })
    .then(res => res.json())
    .then(() => {

        return fetch(QUESTIONS_SAVE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                questions: collectQuestions()
            })
        });

    })
    .then(res => res.json())
    .then(() => {

        alert("Assignment saved successfully ✅");
        window.location.href = BACK_URL;

    })
    .catch(error => {
        console.error(error);
        alert("Failed to save assignment ❌");
    });
}


/* ===============================
   BACK BUTTON
================================ */
function goBack() {
    window.location.href = BACK_URL;
}
