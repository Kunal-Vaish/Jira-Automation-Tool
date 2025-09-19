(() => {
  if (document.getElementById("jira-sidebar-wrapper")) return;

  const defaultTasks = [
    "IA GO over", "Task for Designing and design review", "Third Party Deliverables",
    "Coding", "CHL review", "CRM RT implementation in DEV/SFT Master and VM Tool entry",
    "Self/Peer code review and handling Review comments", "Group CI",
    "Unit/Integration Testing and saving Results in US level in JIRA",
    "Scrum Testing results is Sub task created in JIRA", "Demo to PO (Populated Demo date after mark the US completed)",
    "KT to Smart Ops", "SADT HLD Document Update", "Unit testing data creation",
    "French Translation from BELL", "VM tool entry creation", "Runbook Updates",
    "3rd party deliverables (IES etc)", "Data script document update", "CSM OL / PPOL Specs document updates"
  ];

  const wrapper = document.createElement("div");
  wrapper.id = "jira-sidebar-wrapper";
  wrapper.style.cssText = `
    position: fixed;
    top: 100px;
    left: calc(100vw - 420px);
    width: 400px;
    min-width: 300px;
    max-width: 100vw;
    height: 600px;
    max-height: 100vh;
    z-index: 2147483647;
    box-shadow: 0 0 12px rgba(0,0,0,0.3);
    background: #f9f9f9;
    border: 1px solid #ccc;
    resize: both;
    overflow: auto;
    display: flex;
    flex-direction: column;
    font-family: 'Segoe UI', sans-serif;
    box-sizing: border-box;
  `;

  const spinnerOverlay = document.createElement("div");
  spinnerOverlay.style.cssText = `
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: 2147483646;
    display: none;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    color: white;
    font-family: 'Segoe UI', sans-serif;
  `;
  spinnerOverlay.innerHTML = `
    <div style="
      width: 60px; height: 60px;
      border: 8px solid #f3f3f3;
      border-top: 8px solid #219ebc;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 16px;
    "></div>
    <div style="margin-bottom: 16px; font-size: 16px;">Creating subtasks, please wait...</div>
    <button id="cancelSpinnerBtn" style="
      padding: 10px 20px;
      background: #d00000;
      border: none;
      color: white;
      font-weight: bold;
      border-radius: 4px;
      cursor: pointer;
    ">✖ Cancel</button>
  `;
  document.body.appendChild(spinnerOverlay);

  const spinnerStyle = document.createElement("style");
  spinnerStyle.innerHTML = `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`;
  document.head.appendChild(spinnerStyle);

  let cancelRequested = false;
  spinnerOverlay.querySelector("#cancelSpinnerBtn").onclick = () => {
    cancelRequested = true;
    spinnerOverlay.style.display = "none";
  };

  const header = document.createElement("div");
  header.style.cssText = `
    background: #0047ab;
    color: white;
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: move;
    position: sticky;
    top: 0;
    z-index: 10;
  `;
  header.innerHTML = `
    <h3 style="margin: 0; font-size: 16px;">🧩 Jira Subtask Creator</h3>
    <div>
      <button id="toggleSizeBtn" title="Maximize/Restore" style="background:none;border:none;color:white;font-size:18px;cursor:pointer;margin-right:10px;">🔳</button>
      <button id="closeSidebar" style="background:none;border:none;color:white;font-size:20px;cursor:pointer;">×</button>
    </div>
  `;

  const progressBar = document.createElement("div");
  progressBar.id = "progressBar";
  progressBar.style.cssText = `height: 4px; background: #219ebc; width: 0%; transition: width 0.3s;`;

  const taskControls = document.createElement("div");
  taskControls.style.cssText = `padding: 12px; border-bottom: 1px solid #ccc; display: flex; justify-content: flex-end;`;
  taskControls.innerHTML = `<button type="button" id="toggleAllBtn" style="font-size: 13px; background: none; border: none; color: #0047ab; cursor: pointer;">🚫 Deselect All</button>`;

  const form = document.createElement("form");
  form.id = "subtaskForm";
  form.style.cssText = "flex: 1; display: flex; flex-direction: column; overflow: hidden;";

  const taskInputs = document.createElement("div");
  taskInputs.id = "taskInputs";
  taskInputs.style.cssText = "padding: 12px; flex: 1; overflow-y: auto;";

  const footer = document.createElement("div");
  footer.style.cssText = `padding: 12px; border-top: 1px solid #ddd; background: white; position: sticky; bottom: 0; z-index: 1;`;
  footer.innerHTML = `
    <button type="button" id="previewBtn" style="width: 100%; padding: 10px; background: #ffb703; border: none; font-weight: bold; cursor: pointer;">👁 Preview</button>
    <button type="submit" style="margin-top: 8px; width: 100%; padding: 10px; background: #219ebc; color: white; border: none; font-weight: bold; cursor: pointer;">🚀 Submit</button>
  `;

  const previewBox = document.createElement("div");
  previewBox.id = "previewBox";
  previewBox.style.cssText = "padding: 12px; font-size: 14px; max-height: 200px; overflow-y: auto;";

  document.body.appendChild(wrapper);
  wrapper.appendChild(header);
  wrapper.appendChild(progressBar);
  wrapper.appendChild(taskControls);
  wrapper.appendChild(form);
  form.appendChild(taskInputs);
  form.appendChild(footer);
  form.appendChild(previewBox);

  defaultTasks.forEach((task, i) => {
    const div = document.createElement("div");
    div.style.cssText = "margin-bottom: 10px; display: flex; flex-direction: column;";
    div.innerHTML = `
      <label style="display: flex; align-items: center;">
        <input type="checkbox" id="chk-${i}" checked style="margin-right: 8px;" />
        <input type="text" placeholder="Task name" id="task-${i}" style="flex: 1; padding: 6px; border: 1px solid #ccc; border-radius: 6px;" value="${task}">
      </label>
      <input type="text" placeholder="e.g. 2h, 1d" id="est-${i}" style="margin-top: 6px; width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 6px;" value="">
    `;
    taskInputs.appendChild(div);
  });

  document.getElementById("closeSidebar").onclick = () => wrapper.remove();

  let allChecked = true;
  document.getElementById("toggleAllBtn").onclick = () => {
    allChecked = !allChecked;
    defaultTasks.forEach((_, i) => {
      const cb = document.getElementById(`chk-${i}`);
      if (cb) cb.checked = allChecked;
    });
    document.getElementById("toggleAllBtn").innerText = allChecked ? "🚫 Deselect All" : "✔️ Select All";
  };

  document.getElementById("previewBtn").onclick = () => {
    const btn = document.getElementById("previewBtn");
    if (previewBox.innerHTML) {
      previewBox.innerHTML = "";
      btn.innerText = "👁 Preview";
      return;
    }
    previewBox.innerHTML = "<h4>Preview:</h4><ul style='padding-left: 20px'>";
    defaultTasks.forEach((_, i) => {
      if (!document.getElementById(`chk-${i}`).checked) return;
      const name = document.getElementById(`task-${i}`).value.trim();
      const est = document.getElementById(`est-${i}`).value.trim();
      const status = est ? "To Do" : "In Progress → Cancelled";
      if (name) {
        previewBox.innerHTML += `<li><strong>${name}</strong><br>Estimate: <code>${est || "(none)"}</code> → <b>Status:</b> ${status}</li><br>`;
      }
    });
    previewBox.innerHTML += "</ul>";
    btn.innerText = "🙈 Hide Preview";
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const issueKey = window.location.pathname.split("/").pop();
    const baseUrl = window.location.origin;

    const selectedIndexes = defaultTasks
      .map((_, i) => i)
      .filter(i => document.getElementById(`chk-${i}`).checked && document.getElementById(`task-${i}`).value.trim());

    const total = selectedIndexes.length;
    let createdCount = 0;
    cancelRequested = false;
    progressBar.style.width = "0%";
    spinnerOverlay.style.display = "flex";

    for (let k = 0; k < selectedIndexes.length; k++) {
      if (cancelRequested) break;
      const i = selectedIndexes[k];
      const name = document.getElementById(`task-${i}`).value.trim();
      const est = document.getElementById(`est-${i}`).value.trim();

      const payload = {
        fields: {
          project: { key: issueKey.split("-")[0] },
          parent: { key: issueKey },
          issuetype: { name: "Sub-task" },
          summary: name,
          timetracking: { originalEstimate: est || "0m" }
        }
      };

      try {
        const res = await fetch(`${baseUrl}/rest/api/2/issue`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) continue;
        const data = await res.json();
        createdCount++;
        progressBar.style.width = `${Math.floor((createdCount / total) * 100)}%`;

        if (!est) {
          const transRes = await fetch(`${baseUrl}/rest/api/2/issue/${data.key}/transitions`, { credentials: "include" });
          const transData = await transRes.json();
          const inProgress = transData.transitions.find(t => t.name.toLowerCase() === "in progress");
          const cancelled = transData.transitions.find(t => t.name.toLowerCase() === "cancelled");

          if (inProgress) {
            await fetch(`${baseUrl}/rest/api/2/issue/${data.key}/transitions`, {
              method: "POST", credentials: "include",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ transition: { id: inProgress.id } })
            });
          }

          if (cancelled) {
            await fetch(`${baseUrl}/rest/api/2/issue/${data.key}/transitions`, {
              method: "POST", credentials: "include",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ transition: { id: cancelled.id } })
            });
          }
        }
      } catch {}
    }

    spinnerOverlay.style.display = "none";
    progressBar.style.width = "100%";
    if (createdCount > 0 && !cancelRequested) {
      progressBar.style.backgroundColor = "#2a9d8f";
      progressBar.parentElement.insertAdjacentHTML("beforeend", `
        <div style="text-align: center; padding: 10px; font-weight: bold;">✅ ${createdCount} subtasks created! Refreshing...</div>
      `);
      setTimeout(() => location.reload(), 1000);
    }
  };

  // Dragging
  let isDragging = false, offsetX = 0, offsetY = 0;
  header.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - wrapper.getBoundingClientRect().left;
    offsetY = e.clientY - wrapper.getBoundingClientRect().top;
    document.body.style.userSelect = "none";
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    let newLeft = e.clientX - offsetX;
    let newTop = e.clientY - offsetY;
    const maxLeft = window.innerWidth - wrapper.offsetWidth;
    const maxTop = window.innerHeight - wrapper.offsetHeight;
    const SNAP = 20;

    newLeft = Math.max(0, Math.min(newLeft, maxLeft));
    newTop = Math.max(0, Math.min(newTop, maxTop));

    if (newLeft <= SNAP) newLeft = 0;
    if (newTop <= SNAP) newTop = 0;
    if (Math.abs(newLeft - maxLeft) <= SNAP) newLeft = maxLeft;
    if (Math.abs(newTop - maxTop) <= SNAP) newTop = maxTop;

    wrapper.style.left = `${newLeft}px`;
    wrapper.style.top = `${newTop}px`;
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
    document.body.style.userSelect = "";
  });

  let isMaximized = false;
  document.getElementById("toggleSizeBtn").onclick = () => {
    if (isMaximized) {
      wrapper.style.width = "400px";
      wrapper.style.height = "600px";
      toggleSizeBtn.innerText = "🔳";
    } else {
      wrapper.style.width = "100vw";
      wrapper.style.height = "100vh";
      toggleSizeBtn.innerText = "🗗";
    }
    isMaximized = !isMaximized;
  };
})();
