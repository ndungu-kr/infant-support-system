requireLogin();

// Action labels for display
const actionLabels = {
    feed: "Feed",
    nappy_change: "Nappy Change",
    comfort: "Comfort",
    routine_check: "Routine Check"
};

async function loadCheckins() {
    const checkins = await API.getCheckins();
    const tbody = document.getElementById("checkinsTableBody");

    if (checkins.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No check-ins recorded</td></tr>';
        return;
    }

    tbody.innerHTML = "";

    checkins.forEach(checkin => {
        const row = document.createElement("tr");

        // Time
        const time = new Date(checkin.timestamp);
        const timeStr = time.toLocaleDateString() + " " + time.toLocaleTimeString();

        // Nurse name
        const nurse = checkin.nurseName || "Unregistered tag";

        // Action
        let actionStr = "";
        if (checkin.action) {
            const label = actionLabels[checkin.action] || checkin.action;
            actionStr = '<span class="badge bg-success action-badge">' + label + '</span>';
        } else {
            actionStr =
                '<span class="text-muted me-2">Not recorded</span>' +
                '<div class="btn-group btn-group-sm">' +
                    '<button class="btn btn-outline-primary" onclick="updateAction(' + checkin.id + ', \'feed\')">Feed</button>' +
                    '<button class="btn btn-outline-primary" onclick="updateAction(' + checkin.id + ', \'nappy_change\')">Nappy</button>' +
                    '<button class="btn btn-outline-primary" onclick="updateAction(' + checkin.id + ', \'comfort\')">Comfort</button>' +
                    '<button class="btn btn-outline-primary" onclick="updateAction(' + checkin.id + ', \'routine_check\')">Routine</button>' +
                '</div>';
        }

        row.innerHTML =
            '<td class="small">' + timeStr + '</td>' +
            '<td>' + nurse + '</td>' +
            '<td>' + actionStr + '</td>';

        tbody.appendChild(row);
    });
}

async function updateAction(checkinId, action) {
    await API.updateCheckinAction(checkinId, action);
    loadCheckins();
}

// Initial load
loadCheckins();

// Poll every 10 seconds
setInterval(loadCheckins, 10000);