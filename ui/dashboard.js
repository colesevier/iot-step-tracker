let chart = null;
let currentDevice = null;

const dashTotalStepsEl = document.getElementById("dashTotalSteps");
const dashDurationEl = document.getElementById("dashDuration");
const dashAvgSpmEl = document.getElementById("dashAvgSpm");
const resetUserBtn = document.getElementById("resetUserBtn");

async function loadUsers() {
    const users = ["iphone_browser_1", "iphone_2", "iphone_3"];

    const select = document.getElementById("userSelect");
    select.innerHTML = "";

    users.forEach(u => {
        const opt = document.createElement("option");
        opt.value = u;
        opt.innerText = u;
        select.appendChild(opt);
    });

    currentDevice = users[0];
    select.value = currentDevice;
    select.onchange = () => {
        currentDevice = select.value;
        loadChartData();
    };

    resetUserBtn.onclick = resetCurrentUser;

    await loadChartData();
}

function computeDashboardStats(data) {
    if (!data || data.length === 0) {
        dashTotalStepsEl.textContent = "0";
        dashDurationEl.textContent = "00:00";
        dashAvgSpmEl.textContent = "0";
        return;
    }

    // total steps = sum of steps chunks
    const totalSteps = data.reduce((sum, d) => sum + d.steps, 0);

    const firstTs = new Date(data[0].timestamp);
    const lastTs = new Date(data[data.length - 1].timestamp);
    const diffMs = lastTs - firstTs;
    const diffMin = diffMs > 0 ? diffMs / 60000.0 : 0;

    let durationStr = "00:00";
    if (diffMs > 0) {
        const totalSec = Math.floor(diffMs / 1000);
        const minutes = String(Math.floor(totalSec / 60)).padStart(2, "0");
        const seconds = String(totalSec % 60).padStart(2, "0");
        durationStr = `${minutes}:${seconds}`;
    }

    const avgSpm = diffMin > 0 ? (totalSteps / diffMin) : 0;

    dashTotalStepsEl.textContent = String(totalSteps);
    dashDurationEl.textContent = durationStr;
    dashAvgSpmEl.textContent = Math.round(avgSpm).toString();
}

async function loadChartData() {
    if (!currentDevice) return;

    const data = await fetch(`/user/${encodeURIComponent(currentDevice)}/activity`)
        .then(r => r.json());

    const timestamps = data.map(d => d.timestamp);
    const steps = data.map(d => d.steps);

    computeDashboardStats(data);

    if (!chart) {
        const ctx = document.getElementById('activityChart').getContext('2d');

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: `Steps for ${currentDevice}`,
                    data: steps,
                    borderWidth: 2
                }]
            }
        });
    } else {
        chart.data.labels = timestamps;
        chart.data.datasets[0].label = `Steps for ${currentDevice}`;
        chart.data.datasets[0].data = steps;
        chart.update();
    }
}

async function resetCurrentUser() {
    if (!currentDevice) return;
    try {
        const res = await fetch(`/user/${encodeURIComponent(currentDevice)}/reset`, {
            method: "POST"
        });
        if (!res.ok) {
            console.error("reset user error HTTP", res.status);
            return;
        }
        // Clear chart + stats
        if (chart) {
            chart.data.labels = [];
            chart.data.datasets[0].data = [];
            chart.update();
        }
        computeDashboardStats([]);
    } catch (err) {
        console.error("reset user error", err);
    }
}

loadUsers();
setInterval(loadChartData, 3000);