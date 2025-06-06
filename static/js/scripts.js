document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchJobs");
  const matchBtn = document.getElementById("matchBtn");
  const fileInput = document.getElementById("cvUpload");
  const cvStatus = document.getElementById("cvStatus");
  const allJobs = document.getElementById("allJobs");
  const matchedJobs = document.getElementById("matchedJobs");
  let uploadedCVText = "";

  searchBtn.addEventListener("click", async () => {
    const title = document.getElementById("jobTitle").value;
    const location = document.getElementById("jobLocation").value;

    const res = await fetch(`/api/jobs?title=${title}&location=${location}`);
    const jobs = await res.json();
    allJobs.innerHTML = jobs.map(job =>
      `<div class='job-box'>
        <h4>${job.title}</h4>
        <p><strong>Location:</strong> ${job.location}</p>
        <p><strong>Salary:</strong> £${job.salary_min || "Not listed"}</p>
      </div>`
    ).join('');
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
      alert("Upload your CV first.");
      return;
    }

    const res = await fetch("/api/match_cv_jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cv_text: uploadedCVText }),
    });

    const matches = await res.json();
    matchedJobs.innerHTML = matches.map(match =>
      `<div class='match-box'>
        <h4>${match.title}</h4>
        <p><strong>Location:</strong> ${match.location}</p>
        <p><strong>Match:</strong> ${match.match}%</p>
      </div>`
    ).join('');
  });
});
