
document.addEventListener("DOMContentLoaded", function () {
    const searchBtn = document.getElementById("search-jobs");
    const matchBtn = document.getElementById("match-jobs");
    const uploadBtn = document.getElementById("upload-btn");

    if (searchBtn) {
        searchBtn.addEventListener("click", async () => {
            const title = document.getElementById("job-title").value;
            const location = document.getElementById("job-location").value;
            const response = await fetch(`/api/jobs?title=${title}&location=${location}`);
            const jobs = await response.json();
            displayJobs(jobs, "job-results");
        });
    }

    if (uploadBtn) {
        uploadBtn.addEventListener("click", async () => {
            const fileInput = document.getElementById("cv-input");
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append("cv", file);

            const response = await fetch("/upload_cv", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            document.getElementById("cv-preview").textContent = result.text || "Upload failed.";
        });
    }

    if (matchBtn) {
        matchBtn.addEventListener("click", async () => {
            const cvText = document.getElementById("cv-preview").textContent;
            const response = await fetch("/api/match_cv_jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ cv_text: cvText })
            });
            const matches = await response.json();
            displayMatches(matches, "matched-jobs");
        });
    }

    function displayJobs(jobs, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = "";
        jobs.forEach(job => {
            const card = document.createElement("div");
            card.className = "job-card";
            card.innerHTML = `<strong>${job.title}</strong><br>${job.company} - ${job.location}<br><br>${job.description}`;
            container.appendChild(card);
        });
    }

    function displayMatches(matches, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = "";
        matches.forEach(match => {
            const card = document.createElement("div");
            card.className = "match-card";
            card.innerHTML = `<strong>${match.title}</strong> - ${match.location}<br><strong>Match Score:</strong> ${match.match}%<br><em>${match.reasons.join("; ")}</em>`;
            container.appendChild(card);
        });
    }
});
