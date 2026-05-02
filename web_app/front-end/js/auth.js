// Check if user is logged in, redirect to login if not
async function requireLogin() {
    const session = await API.checkSession();
    if (!session.loggedIn) {
        window.location.href = "index.html";
    }
}

async function handleLogout() {
    await API.logout();
    window.location.href = "index.html";
}