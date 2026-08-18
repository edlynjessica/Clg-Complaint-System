requireLogin();

document
    .getElementById("loadComplaints")
    .addEventListener("click", fetchComplaints);


async function fetchComplaints() {
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

                <p>
                    Assigned Technician:
                    ${complaint.assigned_to || "Not assigned"}
                </p>

                ${
                    complaint.status === "SUBMITTED"
                        ? `
                            <input
                                type="text"
                                id="technician-${complaint.id}"
                                placeholder="Technician ID"
                            >

                            <button
                                onclick="assignTechnician('${complaint.id}')"
                            >
                                Assign Technician
                            </button>
                          `
                        : ""
                }

                ${
                    complaint.status !== "CLOSED" &&
                    complaint.status !== "ESCALATED"
                        ? `
                            <button
                                onclick="escalateComplaint('${complaint.id}')"
                            >
                                Escalate Complaint
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


async function assignTechnician(complaintId) {
    const technicianId = document
        .getElementById(`technician-${complaintId}`)
        .value
        .trim();

    if (!technicianId) {
        document.getElementById("message").textContent =
            "Enter a technician ID";

        return;
    }

    try {
        const data = await apiRequest(
            `/complaints/${complaintId}/assign`,
            {
                method: "PATCH",
                body: JSON.stringify({
                    technician_id: technicianId
                })
            }
        );

        document.getElementById("message").textContent =
            data.message;

        fetchComplaints();

    } catch (error) {
        document.getElementById("message").textContent =
            error.message;
    }
}


async function escalateComplaint(complaintId) {
    try {
        const data = await apiRequest(
            `/complaints/${complaintId}/escalate`,
            {
                method: "PATCH"
            }
        );

        document.getElementById("message").textContent =
            data.message;

        fetchComplaints();

    } catch (error) {
        document.getElementById("message").textContent =
            error.message;
    }
}

document
    .getElementById("loadEscalated")
    .addEventListener("click", loadEscalatedComplaints);


async function loadEscalatedComplaints() {
    const container = document.getElementById("escalatedComplaints");

    try {
        const complaints = await apiRequest("/complaints/");

        const escalated = complaints.filter(
            (complaint) => complaint.status === "ESCALATED"
        );

        if (escalated.length === 0) {
            container.innerHTML = "<p>No escalated complaints.</p>";
            return;
        }

        container.innerHTML = escalated.map((complaint) => `
            <div>
                <h3>${complaint.title}</h3>
                <p>${complaint.description}</p>
                <p>Service: ${complaint.service}</p>
                <p>Location: ${complaint.location}</p>
                <p>Status: ${complaint.status}</p>
                <p>Assigned Technician: ${complaint.assigned_to || "Not assigned"}</p>
            </div>
            <hr>
        `).join("");

    } catch (error) {
        container.innerHTML = `<p>${error.message}</p>`;
    }
}