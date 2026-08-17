requireLogin();

const currentUser = getCurrentUser();

document.getElementById("loadComplaints").addEventListener("click", loadComplaints);

async function loadComplaints() {
    const container = document.getElementById("complaints");

    try {
        const complaints = await apiRequest("/complaints/");

        const assignedComplaints = complaints.filter(
            (complaint) => complaint.assigned_to === currentUser.user_id
        );

        if (assignedComplaints.length === 0) {
            container.innerHTML = "<p>No assigned complaints.</p>";
            return;
        }

        container.innerHTML = assignedComplaints.map((complaint) => `
            <div>
                <h3>${complaint.title}</h3>
                <p>${complaint.description}</p>
                <p>Service: ${complaint.service}</p>
                <p>Location: ${complaint.location}</p>
                <p>Status: ${complaint.status}</p>

                ${
                    complaint.status === "ASSIGNED"
                        ? `
                            <button onclick="updateStatus('${complaint.id}', 'IN_PROGRESS')">
                                Start Work
                            </button>
                          `
                        : ""
                }

                ${
                    complaint.status === "IN_PROGRESS"
                        ? `
                            <button onclick="updateStatus('${complaint.id}', 'RESOLVED')">
                                Resolve Complaint
                            </button>
                          `
                        : ""
                }
            </div>
            <hr>
        `).join("");

    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}

async function updateStatus(complaintId, status) {
    try {
        const data = await apiRequest(
            `/complaints/${complaintId}/status?status=${status}`,
            {
                method: "PATCH"
            }
        );

        document.getElementById("message").textContent = data.message;

        loadComplaints();

    } catch (error) {
        document.getElementById("message").textContent = error.message;
    }
}