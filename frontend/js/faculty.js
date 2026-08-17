document.getElementById("complaintForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = document.getElementById("message");

    try {
        const data = await apiRequest("/complaints/", {
            method: "POST",
            body: JSON.stringify({
                title: document.getElementById("title").value,
                description: document.getElementById("description").value,
                service: document.getElementById("service").value,
                location: document.getElementById("location").value
            })
        });

        message.textContent = data.message;
        event.target.reset();

        loadComplaints();
    } catch (error) {
        message.textContent = error.message;
    }
});


document.getElementById("loadComplaints").addEventListener("click", loadComplaints);


async function loadComplaints() {
    const complaintsContainer = document.getElementById("complaints");

    try {
        const complaints = await apiRequest("/complaints/");

        if (complaints.length === 0) {
            complaintsContainer.innerHTML = "<p>No complaints found.</p>";
            return;
        }

        complaintsContainer.innerHTML = complaints.map((complaint) => `
            <div>
                <h3>${complaint.title}</h3>
                <p>${complaint.description}</p>
                <p>Service: ${complaint.service}</p>
                <p>Location: ${complaint.location}</p>
                <p>Status: ${complaint.status}</p>

                ${
                    complaint.status === "RESOLVED"
                        ? `
                            <button onclick="updateComplaintStatus('${complaint.id}', 'CLOSED')">
                                Verify & Close
                            </button>

                            <button onclick="updateComplaintStatus('${complaint.id}', 'REOPENED')">
                                Reopen
                            </button>
                          `
                        : ""
                }
            </div>
            <hr>
        `).join("");
    } catch (error) {
        complaintsContainer.innerHTML = `<p>${error.message}</p>`;
    }
}


async function updateComplaintStatus(complaintId, status) {
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