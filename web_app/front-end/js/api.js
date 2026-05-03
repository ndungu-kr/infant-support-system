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
        return {
            infantState: "SLEEPING",
            alertLevel: "NONE",
            alertReason: "",
            possibleCauses: [],
            temperature: 22.3,
            humidity: 45.0,
            light: 120,
            loudness: 65,
            motion: 0,
            cameraPresence: "infant_present",
            cameraFaceState: "sleeping",
            cameraCrying: false,
            cameraMotion: null,
            minutesSinceCare: 12,
            cryingDurationMins: 0,
            timestamp: new Date().toISOString(),
            online: true
        };
    },

    getSummary: async function() {
        return {
            cryingEpisodesToday: 3,
            totalCheckinsToday: 8,
            lastCheckinTime: new Date(Date.now() - 720000).toISOString(),
            lastCheckinNurse: "Nurse Smith"
        };
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
        // Generate mock data points every 5 minutes
        const data = [];
        const now = Date.now();
        const interval = 5 * 60 * 1000;
        const count = (hours * 60) / 5;

        for (let i = count; i >= 0; i--) {
            const time = new Date(now - (i * interval));
            data.push({
                temperature: 21 + Math.random() * 3,
                humidity: 40 + Math.random() * 20,
                light: 80 + Math.random() * 200,
                loudness: 30 + Math.random() * 100,
                infantState: ["SLEEPING", "SLEEPING", "AWAKE", "SLEEPING"][Math.floor(Math.random() * 4)],
                timestamp: time.toISOString()
            });
        }
        return data;
    },

    // --- Alerts ---
    getAlerts: async function() {
        return [
            {
                alertLevel: "HIGH",
                alertReason: "Baby has been crying for 6 minutes",
                possibleCauses: ["Possibly hungry (no recent care event logged)"],
                infantState: "CRYING",
                resolved: true,
                resolvedAt: new Date(Date.now() - 3600000).toISOString(),
                timestamp: new Date(Date.now() - 3960000).toISOString()
            },
            {
                alertLevel: "LOW",
                alertReason: "Routine check-in overdue (185 minutes)",
                possibleCauses: [],
                infantState: "SLEEPING",
                resolved: true,
                resolvedAt: new Date(Date.now() - 7200000).toISOString(),
                timestamp: new Date(Date.now() - 7800000).toISOString()
            },
            {
                alertLevel: "LOW",
                alertReason: "Baby is crying (0 mins)",
                possibleCauses: ["Possibly too warm (27.1C)"],
                infantState: "CRYING",
                resolved: false,
                resolvedAt: null,
                timestamp: new Date(Date.now() - 300000).toISOString()
            }
        ];
    },

    // --- Check-ins ---
    getCheckins: async function() {
        return [
            {
                id: 1,
                nurseName: "Nurse Smith",
                action: "feed",
                timestamp: new Date(Date.now() - 720000).toISOString()
            },
            {
                id: 2,
                nurseName: "Nurse Jones",
                action: "routine_check",
                timestamp: new Date(Date.now() - 3600000).toISOString()
            },
            {
                id: 3,
                nurseName: "Nurse Smith",
                action: null,
                timestamp: new Date(Date.now() - 7200000).toISOString()
            }
        ];
    },

    updateCheckinAction: async function(checkinId, action) {
        return { success: true };
    }
};