const API_BASE_URL = "http://localhost:8000";


async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
}

document
    .getElementById("loginForm")
    ?.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document
            .getElementById("email")
            .value
            .trim();

        const password = document
            .getElementById("password")
            .value;

        const message = document.getElementById("message");

        try {
            message.textContent = "Logging in...";

            const data = await apiRequest(
                "/auth/login",
                {
                    method: "POST",
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );

            saveAuth(data);

            const user = getCurrentUser();

            if (user.role === "Faculty / Staff") {
                window.location.href = "faculty.html";
            } else if (user.role === "Service Incharge") {
                window.location.href = "incharge.html";
            } else if (user.role === "Technician") {
                window.location.href = "technician.html";
            } else if (user.role === "Admin") {
                window.location.href = "admin.html";
            }

        } catch (error) {
            message.textContent = error.message;
        }
    });