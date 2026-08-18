requireLogin();


document
    .getElementById("loadComplaints")
    .addEventListener("click", loadComplaints);


async function loadComplaints() {
    const container = document.getElementById("complaints");

    try {
        const complaints = await apiRequest("/complaints/");

        if (complaints.length === 0) {
            container.innerHTML = "<p>No complaints found.</p>";
            return;
        }

        container.innerHTML = complaints.map((complaint) => `
            <div>
                <h3>${complaint.title}</h3>
                <p>${complaint.description}</p>
                <p>Service: ${complaint.service}</p>
                <p>Location: ${complaint.location}</p>
                <p>Status: ${complaint.status}</p>
                <p>Created By: ${complaint.created_by}</p>
                <p>Assigned To: ${complaint.assigned_to || "Not assigned"}</p>
            </div>
            <hr>
        `).join("");

    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}


async function loadStats() {
    try {
        const stats = await apiRequest("/complaints/stats");

        document.getElementById("total").textContent = stats.total;
        document.getElementById("pending").textContent = stats.pending;
        document.getElementById("inProgress").textContent = stats.in_progress;
        document.getElementById("resolved").textContent = stats.resolved;
        document.getElementById("closed").textContent = stats.closed;
        document.getElementById("electrical").textContent = stats.electrical;
        document.getElementById("plumbing").textContent = stats.plumbing;
        document.getElementById("escalated").textContent = stats.escalated;
        document.getElementById("overdue").textContent = stats.overdue;

    } catch (error) {
        document.getElementById("stats").innerHTML =
            `<p>${error.message}</p>`;
    }
}


loadStats();

document
    .getElementById("loadUsers")
    .addEventListener("click", loadUsers);


async function loadUsers() {
    const container = document.getElementById("users");

    try {
        const users = await apiRequest("/auth/users");

        if (users.length === 0) {
            container.innerHTML = "<p>No users found.</p>";
            return;
        }

        container.innerHTML = `
            <div class="user-table-wrapper">
                <table class="user-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Service</th>
                        </tr>
                    </thead>

                    <tbody>
                        ${users.map((user) => `
                            <tr>
                                <td>${user.name || "Unnamed User"}</td>
                                <td>${user.email}</td>
                                <td>${user.role}</td>
                                <td>${user.service || "N/A"}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;

    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}