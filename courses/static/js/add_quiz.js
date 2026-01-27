const COURSE_ID = "{{ course_id }}";
const QUIZ_ID = "{{ quiz_id }}";
const QUIZ_BLOCK = {{ quiz_block|default:"null"|safe }};

let QUIZ_MODE = QUIZ_BLOCK?.quiz_mode || null;
let QUIZ_SCOPE = QUIZ_BLOCK?.scope || "all_before";
let QUESTION_SOURCE = QUIZ_BLOCK?.source || "both";
let ALL_QUESTIONS = [];

document.addEventListener("DOMContentLoaded", () => {
  {% if quiz.title %}
    quizTitle.value = "{{ quiz.title|escapejs }}";
  {% endif %}

  const sourceSelect = document.getElementById("question_source");
  if (sourceSelect) {
    sourceSelect.value = QUESTION_SOURCE;
  }
 
  if (!QUIZ_MODE) {
    new bootstrap.Modal(quizModeModal, { backdrop: "static" }).show();
  } else {
    applyQuizMode(QUIZ_MODE);
  }
});

function selectQuizMode(mode) {
  QUIZ_MODE = mode;
  applyQuizMode(mode);
  bootstrap.Modal.getInstance(quizModeModal)?.hide();
}

function applyQuizMode(mode) {
  ragSection.classList.toggle("d-none", mode !== "auto");
  questionsSection.classList.remove("d-none");
}

function addManualQuestion() {
  ALL_QUESTIONS.push({
    question: "",
    options: { A: "", B: "", C: "", D: "" },
    correct_answer: "A",
    source: "manual"
  });
  renderAllQuestions();
}


function openScopeModal() {
  new bootstrap.Modal(quizScopeModal).show();
}

function confirmScopeAndGenerate() {
  QUIZ_SCOPE = quizScope.value;
  bootstrap.Modal.getInstance(quizScopeModal)?.hide();
  generateAIQuestions();
}

function generateAIQuestions() {
  let count = parseInt(questionCount.value) || 5;

  QUESTION_SOURCE = document.getElementById("question_source").value;

  aiStatus.innerText = "⏳ Generating questions...";
  fetch(
    `http://127.0.0.1:8001/quiz/${QUIZ_ID}/generate` +
    `?scope=${QUIZ_SCOPE}&source=${QUESTION_SOURCE}&mode=auto`,
   {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_questions: count })
   })
  .then(res => res.json())
  .then(data => {
    if (!Array.isArray(data.questions) || data.questions.length === 0) {
      aiStatus.innerText = "⚠️ No questions generated";
      return;
    }
    data.questions.forEach(q => {
      q.source = "ai";
      ALL_QUESTIONS.push(q);
    });
    renderAllQuestions();
    aiStatus.innerText = `✅ ${data.questions.length} questions generated`;
  })
  .catch(() => aiStatus.innerText = "❌ Failed to generate questions");
}


function renderAllQuestions() {
  aiOutput.innerHTML = "";

  ALL_QUESTIONS.forEach((q, i) => {
    aiOutput.innerHTML += `
      <div class="border rounded p-3 mb-3 bg-white">
        <div class="d-flex justify-content-between">
          <strong>Q${i + 1} (${q.source})</strong>
          <button class="btn btn-sm btn-danger"
            onclick="ALL_QUESTIONS.splice(${i},1);renderAllQuestions()">🗑</button>
        </div>

        <textarea class="form-control mt-2"
          onchange="ALL_QUESTIONS[${i}].question=this.value">${q.question}</textarea>

        ${["A","B","C","D"].map(l => `
          <div class="input-group mt-1">
            <span class="input-group-text">${l}</span>
            <input class="form-control" value="${q.options[l]}"
              onchange="ALL_QUESTIONS[${i}].options['${l}']=this.value">
            <span class="input-group-text">
              <input type="radio" name="c_${i}"
                ${q.correct_answer === l ? "checked" : ""}
                onclick="ALL_QUESTIONS[${i}].correct_answer='${l}'">
            </span>
          </div>
        `).join("")}
      </div>
    `;
  });
}


function saveQuiz() {
  if (!quizTitle.value.trim()) {
    alert("Quiz title is required");
    return;
  }

  const payload = {
    title: quizTitle.value,
    quiz_mode: QUIZ_MODE,
    scope: QUIZ_SCOPE,
    question_source: document.getElementById("question_source").value
  };
  
  if (ALL_QUESTIONS.length > 0) {
    payload.questions = ALL_QUESTIONS;
  }
  fetch(`/accounts/instructor/course/${COURSE_ID}/quiz/${QUIZ_ID}/save/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken.value
    },
    body: JSON.stringify(payload)
  })
  .then(res => {
    console.log("SAVE STATUS:", res.status);
    if (!res.ok) throw new Error("Save failed");
    return res.json();
  })
  .then(data => {
    console.log("SAVE RESPONSE:", data);
    alert("Quiz saved ✔");
  })
  .catch(err => {
    console.error("SAVE ERROR:", err);
    alert("Save failed ❌");
  });
}
