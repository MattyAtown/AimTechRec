document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchJobs");
  const matchBtn = document.getElementById("matchBtn");
  const fileInput = document.getElementById("cvUpload");
  const cvStatus = document.getElementById("cvStatus");
  const allJobsDiv = document.getElementById("allJobs");
  const matchedJobsDiv = document.getElementById("matchedJobs");

  let uploadedCVText = "";

  searchBtn.addEventListener("click", async () => {
    const title = document.getElementById("jobTitle").value;
    const location = document.getElementById("jobLocation").value;
    const res = await fetch(`/api/jobs?title=${title}&location=${location}`);
    const jobs = await res.json();

    allJobsDiv.innerHTML = jobs.length
      ? jobs.map(job => `
        <div class="job-box">
          <strong>${job.title}</strong><br>
          Location: ${job.location}<br>
          Salary: £${job.salary_min || "Not listed"}
        </div>`).join('')
      : "<p>No jobs found.</p>";
  });

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("cv", file);

    const res = await fetch("/upload_cv", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    uploadedCVText = data.text;
    cvStatus.textContent = "✅ CV Uploaded";
  });

  matchBtn.addEventListener("click", async () => {
    if (!uploadedCVText) {
      alert("Please upload a CV first.");
      return;
    }

    const res = await fetch("/api/match_cv_jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cv_text: uploadedCVText }),
    });

    const matches = await res.json();

    matchedJobsDiv.innerHTML = matches.length
      ? matches.map(match => `
        <div class="match-box">
          <strong>${match.title}</strong><br>
          Location: ${match.location}<br>
          Salary: £${match.salary || "Not listed"}<br>
          Match: ${match.match}%
        </div>`).join('')
      : "<p>No matched jobs found.</p>";
  });
});
