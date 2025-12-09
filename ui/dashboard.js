// ui/dashboard.js
const SERVER = "http://127.0.0.1:8000";

let chart = null;
let dataTimer = null;
let analyticsTimer = null;

async function loadUsers() {
  const users = ["phone_1", "iphone_browser_1", "phone1", "phone2"];
  const sel = document.getElementById("userSelect");
  sel.innerHTML = "";
  users.forEach(u => {
    const o = document.createElement("option");
    o.value = u;
    o.innerText = u;
    sel.appendChild(o);
  });
  sel.value = users[0];
}

function buildChart(timestamps, steps, device) {
  const ctx = document.getElementById("activityChart").getContext("2d");
  if (chart) {
    chart.data.labels = timestamps;
    chart.data.datasets[0].data = steps;
    chart.data.datasets[0].label = `Steps for ${device}`;
    chart.update();
    return;
  }

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: timestamps,
      datasets: [{
        label: `Steps for ${device}`,
        data: steps,
        borderWidth: 2,
        fill: false,
      }]
    },
    options: {
      scales: {
        x: { display: true, title: { display: true, text: "Time" } },
        y: { display: true, title: { display: true, text: "Steps" } }
      }
    }
  });
}

async function loadActivity() {
  const device = document.getElementById("userSelect").value;
  try {
    const res = await fetch(`${SERVER}/user/${encodeURIComponent(device)}/activity`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const timestamps = data.map(d => d.timestamp);
    const steps = data.map(d => d.steps);
    buildChart(timestamps, steps, device);
  } catch (err) {
    console.error("loadActivity error", err);
  }
}

async function loadAnalytics() {
  const device = document.getElementById("userSelect").value;
  try {
    const res = await fetch(`${SERVER}/analytics/${encodeURIComponent(device)}/today`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const a = await res.json();
    document.getElementById("paceValue").innerText = `${a.pace_spm} spm`;
    document.getElementById("correctedSteps").innerText = a.corrected_steps_today;
    document.getElementById("rawSteps").innerText = `raw: ${a.raw_steps_today}`;
    document.getElementById("caloriesValue").innerText = `${a.calories_today} kcal`;
    document.getElementById("predictionValue").innerText = `${a.predicted_daily_steps}`;
  } catch (err) {
    console.error("loadAnalytics error", err);
  }
}

async function startAutoRefresh() {
  await loadUsers();
  await loadActivity();
  await loadAnalytics();

  dataTimer = setInterval(loadActivity, 3000);
  analyticsTimer = setInterval(loadAnalytics, 5000);

  document.getElementById("refreshBtn").addEventListener("click", () => {
    loadActivity();
    loadAnalytics();
  });

  document.getElementById("userSelect").addEventListener("change", () => {
    loadActivity();
    loadAnalytics();
  });
}

window.onload = startAutoRefresh;
