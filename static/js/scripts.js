document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchJobs");
  const matchBtn = document.getElementById("matchBtn");
  const fileInput = document.getElementById("cvUpload");
  const cvStatus = document.getElementById("cvStatus");
  const resultsDiv = document.getElementById("results");
  let uploadedCVText = "";

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

  const res = await fetch(`/api/jobs?${query}`);

  const res = await fetch(`/api/jobs?title=${title}&location=${location}`);
  const jobs = await res.json();
  renderResults(jobs, []);
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
    renderResults([], matches);
    });

    function renderResults(jobs, matches) {
    resultsDiv.innerHTML = "";

    const container = document.createElement("div");
    container.className = "result-container";

    const leftBox = document.createElement("div");
    leftBox.className = "left-box";
    leftBox.innerHTML = "<h3>Job Listings</h3>";

    const rightBox = document.createElement("div");
    rightBox.className = "right-box";
    rightBox.innerHTML = "<h3>Matched for You</h3>";

    const data = await res.json();
    uploadedCVText = data.text;
    console.log("Uploaded CV Text:", uploadedCVText);
    cvStatus.textContent = "✅ CV Uploaded";

    if (jobs.length === 0) {
      leftBox.innerHTML += "<p>No jobs found.</p>";
    } else {
      jobs.forEach((job) => {
        leftBox.innerHTML += `
          <div class="job-box">
            <h4>${job.title}</h4>
            <p><strong>Location:</strong> ${job.location}</p>
            <p><strong>Salary:</strong> £${job.salary_min || "Not listed"}</p>
            <a href="#">See More</a>
          </div>`;
      });
    }

    if (matches.length === 0) {
      rightBox.innerHTML += "<p>No matched jobs found.</p>";
    } else {
      matches.forEach((match) => {
        rightBox.innerHTML += `
          <div class="match-box">
            <h4>${match.title}</h4>
            <p><strong>Location:</strong> ${match.location}</p>
            <p><strong>Match:</strong> ${match.match}%</p>
            <a href="#">Apply</a>
          </div>`;
      });
    }

    container.appendChild(leftBox);
    container.appendChild(rightBox);
    resultsDiv.appendChild(container);
  }
});
