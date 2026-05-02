// Check login
requireLogin();

// Track previous alert level for audio notification
let previousAlertLevel = "NONE";
let pendingCheckinId = null;

// --- Update Functions ---

function formatNoise(raw) {
    var label;
    if (raw < 50) label = "Quiet";
    else if (raw < 150) label = "Low";
    else if (raw < 300) label = "Moderate";
    else if (raw < 500) label = "Loud";
    else label = "Very Loud";
    return raw + " (" + label + ")";
}

function formatLight(raw) {
    var label;
    if (raw < 100) label = "Dark";
    else if (raw < 300) label = "Dim";
    else if (raw < 600) label = "Moderate";
    else label = "Bright";
    return raw + " (" + label + ")";
}

async function updateStatus() {
    const status = await API.getStatus();

    // Connection status
    const connEl = document.getElementById("connectionStatus");
    if (status.online) {
        connEl.innerHTML = '<span class="status-dot online"></span>System Online';
    } else {
        connEl.innerHTML = '<span class="status-dot offline"></span>System Offline';
    }

    // Infant state display
    const stateEl = document.getElementById("stateDisplay");
    const stateText = status.infantState || "UNKNOWN";
    stateEl.textContent = stateText;
    stateEl.className = "state-display state-" + stateText.toLowerCase();

    // Alert banner
    const alertBanner = document.getElementById("alertBanner");
    const alertLevel = document.getElementById("alertLevel");
    const alertReason = document.getElementById("alertReason");
    const alertCauses = document.getElementById("alertCauses");

    if (status.alertLevel && status.alertLevel !== "NONE") {
        alertBanner.classList.remove("d-none", "alert-high", "alert-low");
        alertBanner.classList.add("alert-" + status.alertLevel.toLowerCase());
        alertLevel.textContent = status.alertLevel + " ALERT: ";
        alertReason.textContent = status.alertReason;

        if (status.possibleCauses && status.possibleCauses.length > 0) {
            alertCauses.textContent = status.possibleCauses.join(" | ");
        } else {
            alertCauses.textContent = "";
        }

        // Play sound if alert just appeared
        if (previousAlertLevel === "NONE" && status.alertLevel !== "NONE") {
            playAlertSound();
        }
    } else {
        alertBanner.classList.add("d-none");
    }

    previousAlertLevel = status.alertLevel || "NONE";

    // Sensor values
    document.getElementById("sensorTemp").textContent = 
        status.temperature !== undefined ? status.temperature.toFixed(1) + " C" : "-";
    document.getElementById("sensorHumidity").textContent = 
        status.humidity !== undefined ? status.humidity.toFixed(1) + " %" : "-";
    document.getElementById("sensorLight").textContent = 
        status.light !== undefined ? formatLight(status.light) : "-";
    document.getElementById("sensorLoudness").textContent = 
        status.loudness !== undefined ? formatNoise(status.loudness) : "-";
    document.getElementById("sensorMotion").textContent = 
        status.motion === 1 ? "Detected" : "None";
    document.getElementById("sensorCare").textContent = 
        status.minutesSinceCare === -1 ? "Never" : status.minutesSinceCare + " min";
    document.getElementById("sensorCamera").textContent = 
        status.cameraPresence === "infant_present" ? "Present" : "Not found";
}

async function updateSummary() {
    const summary = await API.getSummary();

    document.getElementById("cryingEpisodes").textContent = summary.cryingEpisodesToday;
    document.getElementById("totalCheckins").textContent = summary.totalCheckinsToday;

    if (summary.lastCheckinTime) {
        const time = new Date(summary.lastCheckinTime);
        document.getElementById("lastCheckin").textContent = 
            summary.lastCheckinNurse + " at " + time.toLocaleTimeString();
    } else {
        document.getElementById("lastCheckin").textContent = "None today";
    }
}

async function updateCribStatus() {
    const crib = await API.getCribStatus();

    const checkoutBanner = document.getElementById("checkoutBanner");
    const checkoutButtonArea = document.getElementById("checkoutButtonArea");
    const checkoutReasonEl = document.getElementById("checkoutReason");
    const checkoutCountdown = document.getElementById("checkoutCountdown");

    if (crib.checkedOut && !crib.expired) {
        // Baby is checked out
        checkoutBanner.classList.remove("d-none");
        checkoutButtonArea.classList.add("d-none");

        const reasons = {
            feeding: "for feeding",
            bathing: "for bathing",
            medical_check: "for medical check",
            skin_to_skin: "for skin-to-skin contact",
            other: ""
        };
        checkoutReasonEl.textContent = reasons[crib.reason] || "";

        if (crib.expectedReturnAt) {
            const remaining = new Date(crib.expectedReturnAt) - new Date();
            if (remaining > 0) {
                const mins = Math.ceil(remaining / 60000);
                checkoutCountdown.textContent = mins + " minutes remaining";
            } else {
                checkoutCountdown.textContent = "Time expired - please return baby";
                checkoutCountdown.classList.add("text-danger");
            }
        }
    } else {
        checkoutBanner.classList.add("d-none");
        checkoutButtonArea.classList.remove("d-none");
    }
}

async function checkPendingCheckins() {
    const checkins = await API.getCheckins();
    const pending = checkins.find(c => c.action === null);
    const pendingEl = document.getElementById("pendingCheckin");

    if (pending) {
        pendingCheckinId = pending.id;
        pendingEl.classList.remove("d-none");
    } else {
        pendingCheckinId = null;
        pendingEl.classList.add("d-none");
    }
}

// --- Actions ---

async function handleCribCheckout() {
    const reason = document.getElementById("checkoutReason").value;
    const duration = parseInt(document.getElementById("checkoutDuration").value);

    await API.cribCheckout(reason, duration);

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById("checkoutModal"));
    modal.hide();

    // Refresh display
    updateCribStatus();
}

async function handleCribReturn() {
    await API.cribReturn();
    updateCribStatus();
}

async function recordAction(action) {
    if (pendingCheckinId) {
        await API.updateCheckinAction(pendingCheckinId, action);
        checkPendingCheckins();
        updateSummary();
    }
}

function playAlertSound() {
    const audio = document.getElementById("alertSound");
    audio.currentTime = 0;
    audio.play().catch(function() {
        // Browser might block autoplay, that's ok
    });
}

// --- Polling ---

function refreshAll() {
    updateStatus();
    updateSummary();
    updateCribStatus();
    checkPendingCheckins();
}

// Initial load
refreshAll();

// Poll every 10 seconds
setInterval(refreshAll, 10000);