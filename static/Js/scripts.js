document.addEventListener("DOMContentLoaded", () => {
  const searchButton = document.getElementById("searchButton");
  const cvUpload = document.getElementById("cvUpload");
  const jobResults = document.getElementById("jobResults");
  const matchResults = document.getElementById("matchResults");

  // Handle job search
  if (searchButton) {
    searchButton.addEventListener("click", () => {
      const title = document.getElementById("jobTitle").value || "";
      const location = document.getElementById("jobLocation").value || "";

      fetch(`/api/jobs?title=${encodeURIComponent(title)}&location=${encodeURIComponent(location)}`)
        .then((response) => response.json())
        .then((jobs) => {
          jobResults.innerHTML = "";
          if (jobs.length === 0) {
            jobResults.innerHTML = "<p>No results found.</p>";
            return;
          }

          jobs.forEach((job) => {
            const jobCard = document.createElement("div");
            jobCard.className = "job-card";

            jobCard.innerHTML = `
              <h3>${job.title}</h3>
              <p><strong>Company:</strong> ${job.company}</p>
              <p><strong>Location:</strong> ${job.location}</p>
              <p><strong>Industry:</strong> ${job.category}</p>
              <button class="neon-button">Find Out More</button>
            `;
            jobResults.appendChild(jobCard);
          });
        })
        .catch((err) => {
          console.error("Error fetching jobs:", err);
          jobResults.innerHTML = "<p>Error loading job results.</p>";
        });
    });
  }

  // Handle CV upload
  if (cvUpload) {
    cvUpload.addEventListener("change", () => {
      const file = cvUpload.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("cv", file);

      fetch("/upload_cv", {
        method: "POST",
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          matchResults.innerHTML = "";
          if (!data.matches || data.matches.length === 0) {
            matchResults.innerHTML = "<p>No matching jobs found for this CV.</p>";
            return;
          }

          data.matches.forEach((match) => {
            const matchCard = document.createElement("div");
            matchCard.className = "match-card";

            matchCard.innerHTML = `
              <h3>${match.title} (${match.match_percent}% match)</h3>
              <p><strong>Location:</strong> ${match.location}</p>
              <p><strong>Reasons:</strong> ${match.reasons.join(", ")}</p>
              ${match.match_percent < 70 ? '<button onclick="window.location.href=\'/cv_dr.html\'" class="neon-button">Improve CV</button>' : ""}
            `;
            matchResults.appendChild(matchCard);
          });
        })
        .catch((err) => {
          console.error("Error uploading CV:", err);
          matchResults.innerHTML = "<p>There was a problem processing your CV.</p>";
        });
    });
  }
});
