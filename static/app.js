async function fetchArrayStatus() {
  const res = await fetch("/api/array/status");
  const data = await res.json();
  return typeof data.output === "string" ? JSON.parse(data.output) : data.output;
}

async function fetchDisks() {
  const res = await fetch("/api/disks/unassigned");
  const data = await res.json();
  return typeof data.output === "string" ? JSON.parse(data.output) : data.output;
}

async function arrayAction(action) {
  try {
    const res = await fetch(`/api/array/${action}`, { method: "POST" });
    const data = await res.json();
    console.log(`${action} result:`, data);
  } catch (err) {
    console.error(`Failed to ${action}:`, err);
    alert(`Failed to ${action}`);
  }
  await reloadUI();
}

async function startArray() {
  try {
    console.log("Starting array...");
    const startRes = await fetch("/api/array/start", { method: "POST" });
    const startData = await startRes.json();
    console.log("Start result:", startData);
    if (!startData.success) {
      alert("Start failed — aborting start sequence.");
      return;
    }

    console.log("Mounting array...");
    const mountRes = await fetch("/api/array/mount", { method: "POST" });
    const mountData = await mountRes.json();
    console.log("Mount result:", mountData);
  } catch (err) {
    console.error("Failed to start array:", err);
    alert("Failed to start array");
  }
  await reloadUI();
}

async function stopArray() {
  try {
    console.log("Stopping array...");
    const unmountRes = await fetch("/api/array/unmount", { method: "POST" });
    const unmountData = await unmountRes.json();
    console.log("Unmount result:", unmountData);
    if (!unmountData.success) {
      alert("Unmount failed — aborting stop sequence.");
      return;
    }

    const stopRes = await fetch("/api/array/stop", { method: "POST" });
    const stopData = await stopRes.json();
    console.log("Stop result:", stopData);
  } catch (err) {
    console.error("Failed to stop array:", err);
    alert("Failed to stop array");
  }
  await reloadUI();
}

function buildArrayInfoHTML(arrayData) {
  const array = arrayData.array;
  const resync = arrayData.resync;
  const healthClass = array.health.status === "HEALTHY" ? "healthy" : "error";
  let resyncHtml = "";
  if (resync.active) {
    resyncHtml = `
      <p><strong>Parity Action:</strong> <span class="warning">${resync.action}</span></p>
      <p><strong>Parity Progress:</strong> ${resync.progress_percent}%</p>
      <p><strong>Parity ETA:</strong> ${resync.eta_seconds} Seconds</p>
    `;
  }
  return `
    <p><strong>Status:</strong> ${array.state}</p>
    <p><strong>Health:</strong> <span class="${healthClass}">${array.health.status}</span> - ${array.health.details}</p>
    <p><strong>Parity Size:</strong> ${array.size.parity_size_gb} GB</p>
    ${resyncHtml}
    <p><strong>Data Size:</strong> ${array.size.data_gb} GB</p>
  `;
}

function buildArrayDisksHTML(arrayData) {
  return arrayData.disks.map(disk => {
    let fsInfo = "";
    if (disk.filesystem) {
      fsInfo = `<strong>Filesystem:</strong> ${disk.filesystem.type} Mountpoint: ${disk.filesystem.mountpoint} Used: ${disk.filesystem.usage}`;
    }
    return `
      <div class="disk">
        <p><strong>Slot:</strong> ${disk.slot} | <strong>Type:</strong> ${disk.type} | <strong>Device:</strong> ${disk.device} | <strong>Size:</strong> ${disk.size_gb} GB | <strong>Status:</strong> ${disk.status} ${fsInfo}</p>
      </div>
    `;
  }).join("");
}

function buildUnassignedDisksHTML(disksData) {
  function renderDisk(disk, level = 0) {
    const indent = "&nbsp;".repeat(level * 4);
    let html = `<div class="disk" style="margin-left:${level * 10}px;">`;
    html += `<p>${indent}<strong>Device:</strong> ${disk.name} |
            <strong>Type:</strong> ${disk.type} |
            <strong>Size:</strong> ${disk.size} |
            <strong>Mounted at:</strong> ${disk.mountpoint || "Not mounted"}</p>`;
    if (disk.children && disk.children.length > 0) {
      disk.children.forEach(child => {
        html += renderDisk(child, level + 1);
      });
    }
    html += `</div>`;
    return html;
  }

  let html = "";
  disksData.blockdevices.forEach(disk => {
    html += renderDisk(disk);
  });
  return html;
}

function updateButton(array) {
  const container = document.getElementById("start-stop-button");
  if (array.state === "STARTED") {
    container.innerHTML = `<button onclick="stopArray()">Stop Array</button>`;
  } else {
    container.innerHTML = `<button onclick="startArray()">Start Array</button>`;
  }
}

async function reloadUI() {
  try {
    const arrayData = await fetchArrayStatus();
    const diskData = await fetchDisks();
    document.getElementById("array-info").innerHTML = buildArrayInfoHTML(arrayData);
    document.getElementById("disk-info").innerHTML = buildArrayDisksHTML(arrayData);
    document.getElementById("unassigned-disks").innerHTML = buildUnassignedDisksHTML(diskData);
    updateButton(arrayData.array);
  } catch (err) {
    console.error("Failed to load array status:", err);
    document.getElementById("array-info").textContent = "Failed to load array info";
    alert("Failed to load array info");
  }
}

document.getElementById("toggle-advanced").addEventListener("click", () => {
  const menu = document.getElementById("advanced-menu");
  menu.classList.toggle("hidden");
});

window.addEventListener("DOMContentLoaded", reloadUI);
setInterval(reloadUI, 10000);
