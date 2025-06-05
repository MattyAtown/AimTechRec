document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchJobs");
  const matchBtn = document.getElementById("matchBtn");
  const fileInput = document.getElementById("cvUpload");
  const cvStatus = document.getElementById("cvStatus");
  const resultsDiv = document.getElementById("results");
  let uploadedCVText = "";

  // SEARCH JOBS
  searchBtn.addEventListener("click", async () => {
    const title = document.getElementById("jobTitle").value;
    const location = document.getElementById("jobLocation").value;
    const minSalary = document.getElementById("minSalary").value;
    const workType = document.getElementById("workType").value;
    const excludeCompanies = document.getElementById("excludeCompanies").value;

    const query = new URLSearchParams({
      title,
      location,
      min_salary: minSalary,
      work_type: workType,
      exclude_companies: excludeCompanies
    }).toString();

    try {
      const res = await fetch(`/api/jobs?${query}`);
      const jobs = await res.json();
      renderResults(jobs, []);  // Only show jobs on search
    } catch (error) {
      console.error("Error fetching jobs:", error);
    }
  });

  // UPLOAD CV
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("cv", file);

    try {
      const res = await fetch("/upload_cv", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      uploadedCVText = data.text;
      cvStatus.textContent = "✅ CV Uploaded";
    } catch (error) {
      console.error("CV upload error:", error);
      cvStatus.textContent = "❌ Upload Failed";
    }
  });

  // MATCH JOBS
  matchBtn.addEventListener("click", async () => {
    if (!uploadedCVText) {
      alert("Upload your CV first.");
      return;
    }

    try {
      const res = await fetch("/api/match_cv_jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cv_text: uploadedCVText }),
      });

      const matches = await res.json();
      renderResults([], matches);  // Only show matches on Match click
    } catch (error) {
      console.error("Matching error:", error);
    }
  });

  // RENDERING
  function renderResults(jobs, matches) {
    resultsDiv.innerHTML = "";

    const container = document.createElement("div");
    container.className = "result-container";

    const leftBox = document.createElement("div");
    leftBox.className = "left-box";
    leftBox.innerHTML = "<h3>Live Jobs</h3>";

    const rightBox = document.createElement("div");
    rightBox.className = "right-box";
    rightBox.innerHTML = "<h3>Matched for You</h3>";

    jobs.forEach((job) => {
      leftBox.innerHTML += `
        <div class="job-box">
          <h4>${job.title}</h4>
          <p><strong>Location:</strong> ${job.location}</p>
          <p><strong>Salary:</strong> £${job.salary_min || "Not listed"}</p>
          <a href="#">See More</a>
        </div>`;
    });

    matches.forEach((match) => {
      rightBox.innerHTML += `
        <div class="match-box">
          <h4>${match.title}</h4>
          <p><strong>Location:</strong> ${match.location}</p>
          <p><strong>Match Score:</strong> ${match.match_score || match.match}%</p>
          <a href="#">Apply</a>
        </div>`;
    });

    container.appendChild(leftBox);
    container.appendChild(rightBox);
    resultsDiv.appendChild(container);
  }
});
