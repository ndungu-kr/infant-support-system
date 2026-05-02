requireLogin();

// Store chart instances so we can destroy and recreate them
let tempChart = null;
let humidityChart = null;
let noiseChart = null;
let lightChart = null;

async function loadHistory(hours, btnEl) {
    // Update active button
    if (btnEl) {
        document.querySelectorAll(".btn-group .btn").forEach(b => b.classList.remove("active"));
        btnEl.classList.add("active");
    }

    const data = await API.getHistory(hours);

    const labels = data.map(d => {
        const t = new Date(d.timestamp);
        return t.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    });

    // --- State Timeline ---
    buildStateTimeline(data);

    // --- Charts ---
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: {
                ticks: {
                    maxTicksLimit: 8,
                    font: { size: 11 }
                }
            },
            y: {
                beginAtZero: false,
                ticks: {
                    font: { size: 11 }
                }
            }
        },
        elements: {
            point: { radius: 0 },
            line: { borderWidth: 2 }
        }
    };

    // Temperature
    if (tempChart) tempChart.destroy();
    tempChart = new Chart(document.getElementById("tempChart"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Temperature (C)",
                data: data.map(d => d.temperature),
                borderColor: "#dc3545",
                backgroundColor: "rgba(220, 53, 69, 0.1)",
                fill: true
            }]
        },
        options: chartOptions
    });

    // Humidity
    if (humidityChart) humidityChart.destroy();
    humidityChart = new Chart(document.getElementById("humidityChart"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Humidity (%)",
                data: data.map(d => d.humidity),
                borderColor: "#0d6efd",
                backgroundColor: "rgba(13, 110, 253, 0.1)",
                fill: true
            }]
        },
        options: chartOptions
    });

    // Noise
    if (noiseChart) noiseChart.destroy();
    noiseChart = new Chart(document.getElementById("noiseChart"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Noise",
                data: data.map(d => d.loudness),
                borderColor: "#ffc107",
                backgroundColor: "rgba(255, 193, 7, 0.1)",
                fill: true
            }]
        },
        options: chartOptions
    });

    // Light
    if (lightChart) lightChart.destroy();
    lightChart = new Chart(document.getElementById("lightChart"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Light",
                data: data.map(d => d.light),
                borderColor: "#198754",
                backgroundColor: "rgba(25, 135, 84, 0.1)",
                fill: true
            }]
        },
        options: chartOptions
    });
}

function buildStateTimeline(data) {
    const timeline = document.getElementById("stateTimeline");
    timeline.innerHTML = "";

    if (data.length === 0) return;

    // Group consecutive records with the same state
    const segments = [];
    let current = { state: data[0].infantState, count: 1 };

    for (let i = 1; i < data.length; i++) {
        if (data[i].infantState === current.state) {
            current.count++;
        } else {
            segments.push(current);
            current = { state: data[i].infantState, count: 1 };
        }
    }
    segments.push(current);

    // Calculate total data points for proportional sizing
    const total = data.length;

    // State to colour mapping
    const colours = {
        SLEEPING: "#0d6efd",
        AWAKE: "#198754",
        CRYING: "#dc3545",
        ABSENT: "#6c757d",
        UNKNOWN: "#6c757d"
    };

    // Build segments
    segments.forEach(seg => {
        const div = document.createElement("div");
        div.className = "segment";
        div.style.width = ((seg.count / total) * 100) + "%";
        div.style.backgroundColor = colours[seg.state] || "#6c757d";
        div.title = seg.state + " (" + seg.count + " readings)";
        timeline.appendChild(div);
    });
}

// Initial load - 1 hour
loadHistory(1, null);