let structure = PRELOAD || [];
let courseId = COURSE_ID !== "null" ? COURSE_ID : null;
let dragType = null;

document.addEventListener("DOMContentLoaded", () => {
    renderStructure();
    enableDragMenu();
});


/* =========================
   CSRF
========================= */
function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");

    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name)) {
            return c.substring(name.length);
        }
    }
    return "";
}

function renderStructure() {
    const row = document.getElementById("topRow");
    if (!row) return;

    row.innerHTML = "";

    let moduleNum = 1, quizNum = 1, assignNum = 1, liveNum = 1;

    structure.forEach((item, index) => {
        if (item.type === "Module") item.display_title = `Module ${moduleNum++}`;
        if (item.type === "Quiz") item.display_title = `Quiz ${quizNum++}`;
        if (item.type === "Assignment") item.display_title = `Assignment ${assignNum++}`;
        if (item.type === "Live Class") item.display_title = `Live Class ${liveNum++}`;

        row.insertAdjacentHTML("beforeend", blockHTML(item, index));
    });

    row.insertAdjacentHTML(
        "beforeend",
        `<div id="dropZone" class="drop-zone">+</div>`
    );

    enableDropZone();
    enableReorder();
}

function blockHTML(item, index) {
    let colorClass = "";

    if (item.type === "Module") colorClass = "module-card";
    if (item.type === "Quiz") colorClass = "quiz-card";
    if (item.type === "Assignment") colorClass = "assignment-card";
    if (item.type === "Live Class") colorClass = "liveclass-card";

    return `
        <div class="builder-card ${colorClass}" draggable="true" data-index="${index}">
            <div class="card-title">${item.display_title}</div>

            <div class="card-actions">
                ${item.type === "Module"
                    ? `<button class="open-module-btn" onclick="openModule(${index})">Edit</button>`
                    : ""
                }
                ${item.type === "Assignment"
                    ? `<button class="open-module-btn" onclick="openAssignment(${index})">Edit</button>`
                    : ""
                }

                ${item.type === "Quiz" ? `
                    <button class="open-module-btn" onclick="openQuiz(${index})">Open</button>
                ` : ""}

                <button class="delete-module-btn" onclick="deleteBlock(${index})">✖</button>
            </div>
        </div>
    `;
}

function enableDragMenu() {
    document.querySelectorAll(".draggable-btn").forEach(btn => {
        btn.addEventListener("dragstart", () => dragType = btn.dataset.type);
        btn.addEventListener("dragend", () => dragType = null);
    });
}


function enableDropZone() {
    const drop = document.getElementById("dropZone");
    if (!drop) return;

    drop.addEventListener("dragover", e => e.preventDefault());

    drop.addEventListener("drop", () => {
        if (!dragType) return;

        structure.push({
            type: dragType,
            title: "",
            module_id: null,
            quiz_id: null,
            assignment_id: null,
            liveclass_id: null,
            lectures: []
        });

        renderStructure();
    });
}


function enableReorder() {
    document.querySelectorAll(".builder-card").forEach(card => {
        card.addEventListener("dragstart", e => {
            e.dataTransfer.setData("oldIndex", card.dataset.index);
        });

        card.addEventListener("dragover", e => e.preventDefault());

        card.addEventListener("drop", e => {
            const oldIndex = parseInt(e.dataTransfer.getData("oldIndex"));
            const newIndex = parseInt(card.dataset.index);

            if (oldIndex === newIndex) return;

            const moved = structure.splice(oldIndex, 1)[0];
            structure.splice(newIndex, 0, moved);

            renderStructure();
        });
    });
}


function deleteBlock(index) {
    if (!confirm("Delete this item permanently?")) return;

    structure.splice(index, 1);
    renderStructure();
}

function openModule(index) {
    const item = structure[index];

    if (!courseId) {
        alert("Please save the course first!");
        return;
    }

    if (!item.module_id) {
        fetch(`/accounts/instructor/module/create/`, {
            method: "POST",
             headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            credentials: "same-origin",
            body: JSON.stringify({ course_id: courseId })
        })
        .then(r => r.json())
        .then(data => {
            structure[index].module_id = data.module_id;

            saveCourse(() => {
                window.location.href =
                    `/accounts/instructor/courses/${courseId}/module/${data.module_id}/module_add/`;
            });
        });
        return;
    }

    saveCourse(() => {
        window.location.href =
            `/accounts/instructor/courses/${courseId}/module/${item.module_id}/module_add/`;
    });
}

function openQuiz(index) {
    const item = structure[index];

    if (!courseId) {
        alert("Please save the course first!");
        return;
    }

    saveCourse(() => {
        const updated = structure[index];

        if (!updated.quiz_id) {
            alert("Quiz not created yet. Please save again.");
            return;
        }

        window.location.href =
            `/accounts/instructor/course/${courseId}/quiz/${updated.quiz_id}/`;
    });
}

/* =========================
   ASSIGNMENT
========================= */
function openAssignment(index) {
    const item = structure[index];

    if (!courseId) {
        alert("Please save the course first!");
        return;
    }

    if (!item.assignment_id) {
        fetch(`/accounts/instructor/assignment/create/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            credentials: "same-origin",
            body: JSON.stringify({
                course_id: courseId,
                sort_order: index
            })
        })
        .then(r => r.json())
        .then(data => {
            structure[index].assignment_id = data.assignment_id;

            saveCourse(() => {
                window.location.href =
                    `/accounts/instructor/courses/${courseId}/assignment/${data.assignment_id}/edit/`;
            });
        });
        return;
    }

    saveCourse(() => {
        window.location.href =
            `/accounts/instructor/courses/${courseId}/assignment/${item.assignment_id}/edit/`;
    });
}

function saveCourse(callback = null) {
    const level = document.getElementById("courseLevel").value;

    if (!level) {
        alert("Please select a course level");
        return;
    }
    const payload = {
        course_id: courseId,
        title: document.getElementById("courseTitle").value,
        description: document.getElementById("courseDescription").value,
        price: document.getElementById("coursePrice").value,
        category: document.getElementById("courseCategory").value,
        level: level,
        structure: structure
    };

    fetch(`/accounts/instructor/save/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "same-origin",
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Save failed");
        return res.json();
    })
    .then(data => {
        courseId = data.course_id;
        structure = data.structure;

        if (callback) callback();
        else alert("Course Saved!");
        })
    .catch(err => {
        console.error(err);
        alert("Save failed — check server logs");
    });
}


function publishCourse() {
    if (!courseId) {
        alert("Please save before publishing!");
        return;
    }

    saveCourse(() => {
        window.location.href = `/accounts/instructor/publish/${courseId}/`;
    });
}
