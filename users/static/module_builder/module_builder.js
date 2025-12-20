// ===================== GLOBAL ELEMENTS =====================
const container = document.getElementById("topRow");
const buttons = document.querySelectorAll(".draggable-btn");

let draggedType = null;
let filledBoxes = [];
let moduleCount = 0;
let dataSaved = false;

// ===================== DRAG START =====================
buttons.forEach(btn => {
  btn.addEventListener("dragstart", e => {
    draggedType = e.target.dataset.type;
    e.target.classList.add("dragging");
  });

  btn.addEventListener("dragend", e => e.target.classList.remove("dragging"));
});

// ===================== CREATE + BOX =====================
function createPlusBox() {
  const box = document.createElement("div");
  box.className = "plus-box";
  box.innerHTML = `<div class="plus">+</div>`;
  enableDrop(box);
  container.appendChild(box);
}

// ===================== ENABLE DROP =====================
function enableDrop(box) {
  box.addEventListener("dragover", e => {
    e.preventDefault();
    box.classList.add("drag-over");
  });

  box.addEventListener("dragleave", () => box.classList.remove("drag-over"));

  box.addEventListener("drop", () => {
    box.classList.remove("drag-over");
    if (!draggedType) return;

    // SAVE button -> just save structure (like before)
    if (draggedType === "Save") {
      saveData();
      return;
    }

    // avoid overwriting filled box
    if (box.classList.contains("filled")) return;

    // auto name for modules
    let name = "";
    if (draggedType === "Module") {
      name = "Module " + String.fromCharCode(65 + moduleCount);
      moduleCount++;
    } else {
      name = draggedType;
    }

    // visual update
    box.classList.add("filled");
    box.innerHTML = `<div class="box-label">${name}</div>`;

    if (draggedType === "Module") box.classList.add("module-filled");
    if (draggedType === "Quiz") box.classList.add("quiz-filled");
    if (draggedType === "Assignment") box.classList.add("assignment-filled");
    if (draggedType === "Live Class") box.classList.add("liveclass-filled");

    // store for reference (if needed later)
    filledBoxes.push({ type: draggedType, name });

    // click opens module page section (no redirect, no extra logic)
    box.addEventListener("click", () => openModulePage(name));

    // ensure one empty + box exists
    const hasEmpty = [...container.querySelectorAll(".plus-box")]
      .some(b => !b.classList.contains("filled"));

    if (!hasEmpty) createPlusBox();

    enableReorder();
  });
}

// init existing + boxes
document.querySelectorAll(".plus-box").forEach(box => enableDrop(box));

// ===================== REORDER SUPPORT =====================
function enableReorder() {
  const boxes = container.querySelectorAll(".plus-box");

  boxes.forEach(box => {
    box.setAttribute("draggable", "true");

    box.addEventListener("dragstart", e => {
      e.target.classList.add("dragging-box");
    });

    box.addEventListener("dragend", e => {
      e.target.classList.remove("dragging-box");
    });
  });

  container.addEventListener("dragover", e => {
    e.preventDefault();
    const dragging = document.querySelector(".dragging-box");
    const afterElement = getAfterElement(container, e.clientX);

    if (!afterElement) container.appendChild(dragging);
    else container.insertBefore(dragging, afterElement);
  });
}

function getAfterElement(container, x) {
  const elements = [...container.querySelectorAll(".plus-box:not(.dragging-box)")];

  return elements.reduce(
    (closest, child) => {
      const rect = child.getBoundingClientRect();
      const offset = x - rect.left - rect.width / 2;

      if (offset < 0 && offset > closest.offset) {
        return { offset, element: child };
      }
      return closest;
    },
    { offset: Number.NEGATIVE_INFINITY }
  ).element;
}

// ===================== SAVE DATA =====================
function saveData() {
  if (filledBoxes.length === 0) {
    alert("⚠️ No modules to save!");
    return;
  }

  console.log("Saved Data:", filledBoxes);
  alert("✔ Structure Saved!");

  dataSaved = true;
}

// ===================== OPEN MODULE PAGE (JUST SWITCH VIEW) =====================
function openModulePage(name) {
  if (!dataSaved) {
    alert("Save the module structure first!");
    return;
  }

  console.log("Opening module page for:", name);

  document.getElementById("builderSection").style.display = "none";
  document.getElementById("modulePageSection").style.display = "block";

  // module_page.js will behave exactly as before:
  // user will click ➕ Add Lecture, Save, Post, etc.
}

console.log("Builder Logic Ready");
