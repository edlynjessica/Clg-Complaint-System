requireLogin();

document.getElementById("loadComplaints").addEventListener("click", loadComplaints);

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