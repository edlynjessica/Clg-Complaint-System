function saveAuth(data) {
    localStorage.setItem("access_token", data.access_token);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}