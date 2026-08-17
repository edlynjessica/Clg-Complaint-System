function saveAuth(data) {
    localStorage.setItem("access_token", data.access_token);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function getCurrentUser() {
    const token = getToken();

    if (!token) {
        return null;
    }

    try {
        const payload = JSON.parse(atob(token.split(".")[1]));

        return {
            user_id: payload.user_id,
            role: payload.role
        };
    } catch {
        return null;
    }
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}

function requireLogin() {
    if (!getToken()) {
        window.location.href = "login.html";
    }
}