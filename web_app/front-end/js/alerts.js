requireLogin();

async function loadAlerts() {
    const alerts = await API.getAlerts();
    const tbody = document.getElementById("alertsTableBody");

    if (alerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No alerts recorded</td></tr>';
        return;
    }

    tbody.innerHTML = "";

    alerts.forEach(alert => {
        const row = document.createElement("tr");

        // Time
        const time = new Date(alert.timestamp);
        const timeStr = time.toLocaleDateString() + " " + time.toLocaleTimeString();

        // Level badge
        let badgeClass = "bg-secondary";
        if (alert.alertLevel === "HIGH") badgeClass = "bg-danger";
        else if (alert.alertLevel === "LOW") badgeClass = "bg-warning text-dark";

        // Possible causes
        let causesStr = "-";
        if (alert.possibleCauses && alert.possibleCauses.length > 0) {
            causesStr = alert.possibleCauses.join(", ");
        }

        // Status
        let statusStr = "";
        if (alert.resolved) {
            const resolvedTime = new Date(alert.resolvedAt);
            statusStr = '<span class="text-success">Resolved</span><br><small class="text-muted">' +
                resolvedTime.toLocaleTimeString() + '</small>';
        } else {
            statusStr = '<span class="badge bg-danger">Active</span>';
        }

        // State badge
        let stateClass = "bg-secondary";
        if (alert.infantState === "CRYING") stateClass = "bg-danger";
        else if (alert.infantState === "SLEEPING") stateClass = "bg-primary";
        else if (alert.infantState === "AWAKE") stateClass = "bg-success";
        else if (alert.infantState === "ABSENT") stateClass = "bg-danger";

        row.innerHTML =
            '<td class="small">' + timeStr + '</td>' +
            '<td><span class="badge ' + badgeClass + '">' + alert.alertLevel + '</span></td>' +
            '<td>' + alert.alertReason + '</td>' +
            '<td class="small">' + causesStr + '</td>' +
            '<td><span class="badge ' + stateClass + '">' + alert.infantState + '</span></td>' +
            '<td>' + statusStr + '</td>';

        tbody.appendChild(row);
    });
}

// Initial load
loadAlerts();

// Poll every 10 seconds
setInterval(loadAlerts, 10000);