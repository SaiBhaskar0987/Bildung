const workspace = document.getElementById("workspace");
const addModuleBtn = document.getElementById("addModuleBtn");
const saveBtn = document.getElementById("saveBtn");
const editBtn = document.getElementById("editBtn");
const postBtn = document.getElementById("postBtn");
const output = document.getElementById("output");

const moduleModal = document.getElementById("moduleModal");
const moduleNameInput = document.getElementById("moduleNameInput");
const createModuleBtn = document.getElementById("createModuleBtn");
const cancelModuleBtn = document.getElementById("cancelModuleBtn");

let modules = [];

// === Show modal ===
addModuleBtn.addEventListener("click", () => {
  moduleNameInput.value = "";
  moduleModal.style.display = "flex";
  moduleNameInput.focus();
});

// === Cancel modal ===
cancelModuleBtn.addEventListener("click", () => {
  moduleModal.style.display = "none";
});

// === Create module ===
createModuleBtn.addEventListener("click", () => {
  const name = moduleNameInput.value.trim();
  if (!name) {
    alert("Please enter a module name!");
    return;
  }
  createModule(name);
  moduleModal.style.display = "none";
  saveBtn.classList.remove("inactive");
  postBtn.classList.remove("inactive");
});

function createModule(moduleName) {
  const moduleCard = document.createElement("div");
  moduleCard.classList.add("module");
  moduleCard.innerHTML = `
    <h2>${moduleName}</h2>
    <div class="lectures"></div>
    <button class="addLectureBtn">+ Add Lecture</button>
  `;

  workspace.appendChild(moduleCard);
  makeEditable(moduleCard);

  // Add first lecture by default
  addLecture(moduleCard);

  // Add lecture button
  const addLectureBtn = moduleCard.querySelector(".addLectureBtn");
  addLectureBtn.addEventListener("click", () => addLecture(moduleCard));
}

// === Add lecture section with description ===
function addLecture(moduleCard) {
  const lecturesContainer = moduleCard.querySelector(".lectures");

  const lectureDiv = document.createElement("div");
  lectureDiv.classList.add("lecture");
  lectureDiv.innerHTML = `
    <input type="text" placeholder="Lecture name" class="lecture-input" />
    <label class="upload">
      📄 Upload PDF
      <input type="file" accept=".pdf" class="pdf-upload" />
    </label>
    <label class="upload">
      🎥 Upload Video
      <input type="file" accept="video/*" class="video-upload" />
    </label>
    <textarea placeholder="📝 Write a small description about this lecture..." class="lecture-desc"></textarea>
    <button class="removeLectureBtn">❌ Remove</button>
  `;

  lecturesContainer.appendChild(lectureDiv);

  // Remove lecture
  lectureDiv.querySelector(".removeLectureBtn").addEventListener("click", () => {
    lectureDiv.remove();
  });
}

// === Allow editing ===
function makeEditable(moduleCard) {
  editBtn.addEventListener("click", () => {
    const isEditable = moduleCard.getAttribute("contenteditable") === "true";
    moduleCard.setAttribute("contenteditable", !isEditable);
    moduleCard.style.border = !isEditable ? "2px solid #5b8def" : "none";
  });
}

// === Save data ===
saveBtn.addEventListener("click", () => {
  modules = [];
  document.querySelectorAll(".module").forEach(mod => {
    const name = mod.querySelector("h2").textContent;
    const lectures = [];
    mod.querySelectorAll(".lecture").forEach(lec => {
      const lectureName = lec.querySelector(".lecture-input").value;
      const pdfFile = lec.querySelector(".pdf-upload").files[0];
      const videoFile = lec.querySelector(".video-upload").files[0];
      const desc = lec.querySelector(".lecture-desc").value;

      const pdfUrl = pdfFile ? URL.createObjectURL(pdfFile) : "";
      const videoUrl = videoFile ? URL.createObjectURL(videoFile) : "";

      lectures.push({ lectureName, pdfUrl, videoUrl, desc });
    });
    modules.push({ name, lectures });
  });

  localStorage.setItem("modules", JSON.stringify(modules));
  alert("✅ Modules saved successfully!");
});

// === Post data ===
postBtn.addEventListener("click", () => {
  const saved = JSON.parse(localStorage.getItem("modules") || "[]");
  if (saved.length === 0) {
    alert("⚠️ No modules to post!");
    return;
  }

  output.style.display = "flex";
  output.innerHTML = "<h3>📦 Posted Modules:</h3>";

  saved.forEach((m, i) => {
    const moduleButton = document.createElement("button");
    moduleButton.classList.add("posted-module-btn");
    moduleButton.textContent = `${i + 1}. ${m.name}`;
    moduleButton.style.display = "block";
    moduleButton.style.margin = "8px 0";
    moduleButton.style.padding = "5px 10px";
    moduleButton.style.background = "#5b8def";
    moduleButton.style.color = "black";
    moduleButton.style.border = "none";
    moduleButton.style.borderRadius = "6px";
    moduleButton.style.cursor = "pointer";

    moduleButton.addEventListener("click", () => showLectures(m));
    output.appendChild(moduleButton);
  });
});

// === Show lectures of a module ===
function showLectures(module) {
  output.innerHTML = `<h3>${module.name} — Lectures</h3>`;

  module.lectures.forEach((lec, j) => {
    const lecDiv = document.createElement("div");
    lecDiv.style.marginBottom = "12px";
    lecDiv.style.padding = "10px";
    lecDiv.style.border = "1px solid #ddd";
    lecDiv.style.borderRadius = "6px";

    lecDiv.innerHTML = `
      <strong>Lecture ${j + 1}:</strong> ${lec.lectureName || "(No name)"}<br>
      📝 ${lec.desc || "(No description)"}<br>
      ${lec.pdfUrl ? `<button class="viewPdfBtn">📄 Open PDF</button>` : ""}
      ${lec.videoUrl ? `<button class="viewVideoBtn">🎥 Open Video</button>` : ""}
    `;

    // PDF open
    const pdfBtn = lecDiv.querySelector(".viewPdfBtn");
    if (pdfBtn) {
      pdfBtn.addEventListener("click", () => {
        output.innerHTML = `
          <h3>${lec.lectureName} — PDF View</h3>
          <iframe src="${lec.pdfUrl}" width="100%" height="500px"></iframe>
        `;
        addBackButton(() => showLectures(module));
      });
    }

    // Video open
    const videoBtn = lecDiv.querySelector(".viewVideoBtn");
    if (videoBtn) {
      videoBtn.addEventListener("click", () => {
        output.innerHTML = `
          <h3>${lec.lectureName} — Video View</h3>
          <video src="${lec.videoUrl}" controls width="100%" height="500"></video>
        `;
        addBackButton(() => showLectures(module));
      });
    }

    output.appendChild(lecDiv);
  });

  addBackButton(() => postBtn.click());
}

// === Back button helper ===
function addBackButton(callback) {
  const backBtn = document.createElement("button");
  backBtn.textContent = "⬅ Back";
  backBtn.style.marginTop = "10px";
  backBtn.style.padding = "5px 10px";
  backBtn.style.background = "#333";
  backBtn.style.color = "white";
  backBtn.style.border = "none";
  backBtn.style.borderRadius = "6px";
  backBtn.style.cursor = "pointer";
  backBtn.addEventListener("click", callback);
  output.appendChild(backBtn);
}
