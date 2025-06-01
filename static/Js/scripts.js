
document.addEventListener("DOMContentLoaded", () => {
    const searchBtn = document.getElementById("search-btn");
    const uploadCvInput = document.getElementById("cv-upload");
    const searchResultsDiv = document.getElementById("search-results");
    const matchResultsDiv = document.getElementById("match-results");

    if (searchBtn) {
        searchBtn.addEventListener("click", async () => {
            const jobTitle = document.getElementById("job-title").value.trim();
            const location = document.getElementById("location").value.trim();

            const queryParams = new URLSearchParams();
            if (jobTitle) queryParams.append("title", jobTitle);
            if (location) queryParams.append("location", location);

            const response = await fetch(`/api/jobs?${queryParams}`);
            const jobs = await response.json();
            renderJobs(jobs, searchResultsDiv);
        });
    }

    function renderJobs(jobs, container) {
        container.innerHTML = "";
        if (!jobs.length) {
            container.innerHTML = "<p>No jobs found.</p>";
            return;
        }
        jobs.forEach(job => {
            const jobCard = document.createElement("div");
            jobCard.className = "job-card";
            jobCard.innerHTML = `
                <h3>${job.title}</h3>
                <p><strong>Company:</strong> ${job.company || "N/A"}</p>
                <p><strong>Location:</strong> ${job.location || "N/A"}</p>
                <p><strong>Category:</strong> ${job.category || "N/A"}</p>
                <p><strong>Contract:</strong> ${job.contract_time || "N/A"}</p>
                <p><strong>Salary:</strong> £${job.salary_min?.toFixed(2) || "N/A"}</p>
            `;
            container.appendChild(jobCard);
        });
    }

    if (uploadCvInput) {
        uploadCvInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = () => {
                    const resultBox = document.getElementById("cv-review-box");
                    if (resultBox) {
                        resultBox.innerText = "Uploaded CV: " + file.name;
                        resultBox.style.display = "block";
                    }
                };
                reader.readAsText(file);
            }
        });
    }
});
