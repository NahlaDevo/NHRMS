const API_BASE = "http://127.0.0.1:8000/api";

function getToken() {
    return localStorage.getItem("token");
}

function getUsername() {
    return localStorage.getItem("username");
}

function getUserRole() {
    return localStorage.getItem("role");
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    return getUserRole() === "admin";
}

function setAuth(token, username, role) {
    localStorage.setItem("token", token);
    localStorage.setItem("username", username);
    localStorage.setItem("role", role);
}

function clearAuth() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
}

function logout() {
    clearAuth();
    window.location.href = "/static/pages/login.html";
}

function redirectIfNotLoggedIn() {
    if (!isLoggedIn()) {
        window.location.href = "/static/pages/login.html";
        return false;
    }
    return true;
}

async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const options = { method, headers };
    if (body && method !== "GET") {
        options.body = JSON.stringify(body);
    }
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }
        return data;
    } catch (error) {
        if (error.message.includes("401") || error.message.includes("Invalid")) {
            clearAuth();
            window.location.href = "/static/pages/login.html";
        }
        throw error;
    }
}
