const SERVER = "http://127.0.0.1:8000";

let chart = null;

async function loadUsers() {
    // Users = keys of activity data
    const activity = await fetch(`${SERVER}/user/phone1/activity`).then(r => r.json());
    // For demo we assume known users:
    const users = ["phone1", "phone2", "phone3"];

    const select = document.getElementById("userSelect");
    select.innerHTML = "";

    users.forEach(u => {
        const opt = document.createElement("option");
        opt.value = u;
        opt.innerText = u;
        select.appendChild(opt);
    });

    select.onchange = loadChartData;
}

async function loadChartData() {
    const device = document.getElementById("userSelect").value;
    const data = await fetch(`${SERVER}/user/${device}/activity`).then(r => r.json());

    const timestamps = data.map(d => d.timestamp);
    const steps = data.map(d => d.steps);

    if (!chart) {
        const ctx = document.getElementById('activityChart').getContext('2d');

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: `Steps for ${device}`,
                    data: steps,
                    borderWidth: 2
                }]
            }
        });
    } else {
        chart.data.labels = timestamps;
        chart.data.datasets[0].data = steps;
        chart.update();
    }
}

loadUsers();
setInterval(loadChartData, 3000); // update every 3 seconds
