// ============================================
// API Module - Mock data for development
// When backend is ready, replace mock returns
// with fetch() calls to the real API
// ============================================

const API_BASE = "http://localhost:8080"; // Change to OpenShift URL later

function authHeaders() {
    const token = localStorage.getItem("jwt");
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    };
}

const API = {

    // --- Auth ---
    login: async function(username, password) {
        const res = await fetch(API_BASE + "/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });
        const data = await res.json();
        if (data.token) {
            localStorage.setItem("jwt", data.token);
            localStorage.setItem("nurseName", data.name);
            return { success: true };
        }
        return { success: false, error: data.error };
    },

    logout: async function() {
        const token = localStorage.getItem("jwt");
        await fetch(API_BASE + "/logout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            }
        });
        localStorage.removeItem("jwt");
        localStorage.removeItem("nurseName");
        return { success: true };
    },

    checkSession: async function() {
        const token = localStorage.getItem("jwt");
        if (!token) return { loggedIn: false };
        const res = await fetch(API_BASE + "/status", {
            headers: { "Authorization": "Bearer " + token }
        });
        return { loggedIn: res.ok };
    },

    // --- Dashboard ---
    getStatus: async function() {
        const res = await fetch(API_BASE + "/status", {
            headers: authHeaders()
        });
        return await res.json();
    },

    getSummary: async function() {
        const res = await fetch(API_BASE + "/summary", {
            headers: authHeaders()
        });
        return await res.json();
    },

    // --- Crib Status ---
    getCribStatus: async function() {
        const res = await fetch(API_BASE + "/crib-status", {
            headers: authHeaders()
        });
        return await res.json();
    },

    cribCheckout: async function(reason, durationMinutes) {
        const res = await fetch(API_BASE + "/crib-checkout", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ reason: reason, durationMinutes: durationMinutes })
        });
        return await res.json();
    },

    cribReturn: async function() {
        const res = await fetch(API_BASE + "/crib-return", {
            method: "POST",
            headers: authHeaders()
        });
        return await res.json();
    },

    // --- History ---
    getHistory: async function(hours) {
        const now = new Date();
        const start = new Date(now.getTime() - hours * 60 * 60 * 1000);
        const startStr = start.toISOString().split("T")[0];
        const endStr = now.toISOString().split("T")[0];
        const res = await fetch(API_BASE + "/history?start=" + startStr + "&end=" + endStr, {
            headers: authHeaders()
        });
        return await res.json();
    },

    // --- Alerts ---
    getAlerts: async function() {
        const now = new Date();
        const weekAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000); // alerts for past 3 days
        const startStr = weekAgo.toISOString().split("T")[0];
        const endStr = now.toISOString().split("T")[0];
        const res = await fetch(API_BASE + "/alert?start=" + startStr + "&end=" + endStr, {
            headers: authHeaders()
        });
        return await res.json();
    },

    // --- Check-ins ---
    getCheckins: async function() {
        const now = new Date();
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const startStr = weekAgo.toISOString().split("T")[0];
        const endStr = now.toISOString().split("T")[0];
        const res = await fetch(API_BASE + "/checkins?start=" + startStr + "&end=" + endStr, {
            headers: authHeaders()
        });
        return await res.json();
    },

    updateCheckinAction: async function(checkinId, action) {
        const res = await fetch(API_BASE + "/checkin/update", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ id: checkinId, action: action })
        });
        return await res.json();
    }
};