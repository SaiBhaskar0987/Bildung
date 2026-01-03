document.addEventListener("DOMContentLoaded", () => {

    const addLectureBtn = document.getElementById("addLecture");

    addLectureBtn.addEventListener("click", () => {
        addNewLectureCard();
    });

});

function addNewLectureCard() {

    const list = document.getElementById("lectureList");

    const card = document.createElement("div");
    card.className = "lecture-card";

    card.innerHTML = `
        <div class="lecture-header">
            <span class="lecture-title">New Lecture</span>
            <button type="button"
                    class="delete-lecture-btn"
                    onclick="this.closest('.lecture-card').remove()">✖</button>
        </div>

        <div class="lecture-body">

            <label>Lecture Title</label>
            <input type="text"
                   class="lecture-title-input"
                   placeholder="Enter lecture title">

            <label>Upload Video</label>
            <input type="file"
                   class="lecture-video-input"
                   accept="video/*">

            <label>Upload PDF</label>
            <input type="file"
                   class="lecture-file-input"
                   accept="application/pdf">

        </div>
    `;

    list.appendChild(card);
}


function saveModule() {

    const fd = new FormData();

    const moduleTitle = document.getElementById("moduleTitle").value.trim();
    const moduleDescription = document.getElementById("moduleDescription").value.trim();

    fd.append("module_title", moduleTitle);
    fd.append("description", moduleDescription);

    const cards = document.querySelectorAll(".lecture-card");
    fd.append("lecture_count", cards.length);

    cards.forEach((card, index) => {

        const titleInput = card.querySelector(".lecture-title-input");
        const videoInput = card.querySelector(".lecture-video-input");
        const pdfInput = card.querySelector(".lecture-file-input");

        fd.append(`lecture_title_${index}`, titleInput.value.trim());

        if (videoInput && videoInput.files.length > 0) {
            fd.append(`lecture_video_${index}`, videoInput.files[0]);
        }

        if (pdfInput && pdfInput.files.length > 0) {
            fd.append(`lecture_pdf_${index}`, pdfInput.files[0]);
        }
    });

    fetch(`${BASE_URL}/module/${MODULE_ID}/save/`, {
        method: "POST",
        body: fd
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert("Module saved (draft)");
            goBack();
        } else {
            alert("Save failed");
        }
    })
    .catch(err => {
        console.error(err);
        alert("Server error while saving module");
    });
}

function goBack() {
    window.location.href = `/accounts/instructor/courses/add/?course_id=${COURSE_ID}`;
}