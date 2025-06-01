
document.addEventListener("DOMContentLoaded", function () {
    const searchBtn = document.getElementById("search-btn");
    const jobResults = document.getElementById("job-results");
    const uploadBtn = document.getElementById("upload-btn");
    const cvInput = document.getElementById("cv-input");
    const cvPreview = document.getElementById("cv-preview");

    if (searchBtn) {
        searchBtn.addEventListener("click", async () => {
            const title = document.getElementById("job-title").value;
            const location = document.getElementById("location").value;
            const response = await fetch(`/api/jobs?title=${encodeURIComponent(title)}&location=${encodeURIComponent(location)}`);
            const jobs = await response.json();
            jobResults.innerHTML = "";

            if (jobs.length === 0) {
                jobResults.innerHTML = "<p>No matching jobs found.</p>";
                return;
            }

            jobs.forEach(job => {
                const div = document.createElement("div");
                div.className = "job-card";
                div.innerHTML = `
                    <strong>${job.title}</strong><br>
                    ${job.location}<br>
                    <span class="match">Match: ~80%</span><br>
                    <em>${job.category}</em>
                `;
                jobResults.appendChild(div);
            });
        });
    }

    if (uploadBtn && cvInput) {
        uploadBtn.addEventListener("click", async () => {
            const file = cvInput.files[0];
            if (!file) {
                alert("Please select a CV to upload.");
                return;
            }

            const formData = new FormData();
            formData.append("cv", file);

            try {
                const response = await fetch("/upload_cv", {
                    method: "POST",
                    body: formData
                });

                const text = await response.text();
                cvPreview.textContent = text || "No preview available.";
            } catch (error) {
                console.error("CV upload failed:", error);
                cvPreview.textContent = "Error uploading CV.";
            }
        });
    }
});
