
document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchJobs");
  const matchBtn = document.getElementById("matchBtn");
  const fileInput = document.getElementById("cvUpload");
  const cvStatus = document.getElementById("cvStatus");
  const allJobsDiv = document.getElementById("allJobs");
  const matchedJobsDiv = document.getElementById("matchedJobs");
  const popup = document.getElementById("popup");
  let uploadedCVText = "";
  let selectedJob = null;

  searchBtn.addEventListener("click", async () => {
    const title = document.getElementById("jobTitle").value;
    const location = document.getElementById("jobLocation").value;
    const minSalary = document.getElementById("minSalary").value;
    const idealSalary = document.getElementById("idealSalary").value;
    const workType = document.getElementById("workType").value;
    const benefits = Array.from(document.getElementById("benefits").selectedOptions).map(opt => opt.value);
    const exclude = document.getElementById("excludeCompanies").value;

    const query = new URLSearchParams({
      title,
      location,
      min_salary: minSalary,
      ideal_salary: idealSalary,
      work_type: workType,
      benefits: benefits.join(','),
      exclude_companies: exclude
    }).toString();

    const res = await fetch(`/api/jobs?${query}`);
    const jobs = await res.json();
    renderJobs(jobs, allJobsDiv);
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
    renderJobs(matches, matchedJobsDiv, true);
  });

  function renderJobs(jobs, container, isMatch = false) {
    container.innerHTML = "";
    if (jobs.length === 0) {
      container.innerHTML = "<p>No jobs found.</p>";
      return;
    }

    jobs.forEach((job) => {
      const box = document.createElement("div");
      box.className = "job-box";
      box.innerHTML = `
        <h4>${job.title}</h4>
        <p><strong>Location:</strong> ${job.location}</p>
        <p><strong>Salary:</strong> £${job.salary || "Not listed"}</p>
        ${isMatch ? `<p><strong>Match:</strong> ${job.match}%</p>` : ""}
      `;
      box.addEventListener("click", () => showPopup(job));
      container.appendChild(box);
    });
  }

  function showPopup(job) {
    selectedJob = job;
    popup.innerHTML = `
      <div class="popup-overlay">
        <div class="popup-content">
          <span class="close-btn" onclick="document.getElementById('popup').innerHTML=''">&times;</span>
          <h3>${job.title} – ${job.location}</h3>
          <p><strong>Salary:</strong> £${job.salary || "Not listed"}</p>
          <p>${job.description || "No description provided."}</p>
          <label><input type="checkbox" id="confirmShortlist"> Shortlist me for this role</label><br><br>
          <button onclick="submitShortlist()">Submit</button>
        </div>
      </div>
    `;
  }

  window.submitShortlist = async function () {
    const confirm = document.getElementById("confirmShortlist").checked;
    if (!confirm || !selectedJob) {
      alert("Please tick the box to confirm.");
      return;
    }
    const res = await fetch("/shortlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(selectedJob),
    });
    const result = await res.json();
    alert(result.message);
    popup.innerHTML = "";
  };
});
