// scripts.js

document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchJobs");
  const resultsDiv = document.getElementById("results");
  const matchBtn = document.getElementById("matchBtn");
  const fileInput = document.getElementById("cvUpload");
  const cvStatus = document.getElementById("cvStatus");
  let uploadedCVText = "";

  searchBtn?.addEventListener("click", async function () {
    const title = document.getElementById("jobTitle").value;
    const location = document.getElementById("jobLocation").value;

    const res = await fetch(`/api/jobs?title=${title}&location=${location}`);
    const jobs = await res.json();
    displayJobs(jobs);
  });

  fileInput?.addEventListener("change", async function () {
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
    cvStatus.innerHTML = "✅ CV Uploaded";
  });

  matchBtn?.addEventListener("click", async function () {
    if (!uploadedCVText) {
      alert("Upload your CV first");
      return;
    }

    const res = await fetch("/api/match_cv_jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cv_text: uploadedCVText }),
    });
    const matches = await res.json();
    displayMatches(matches);
  });

  function displayJobs(jobs) {
    const jobList = document.createElement("div");
    jobList.className = "job-list";
    if (jobs.length === 0) {
      jobList.innerHTML = "<p>No jobs found.</p>";
    } else {
      jobs.forEach((job) => {
        const div = document.createElement("div");
        div.className = "job-box";
        div.innerHTML = `
          <h4>${job.title}</h4>
          <p><strong>Location:</strong> ${job.location}</p>
          <p><strong>Salary:</strong> £${job.salary_min || "Not listed"}</p>
          <a href="#">See More</a>
        `;
        jobList.appendChild(div);
      });
    }
    updateResults(jobList, null);
  }

  function displayMatches(matches) {
    const matchList = document.createElement("div");
    matchList.className = "match-list";
    if (matches.length === 0) {
      matchList.innerHTML = "<p>No matched jobs.</p>";
    } else {
      matches.forEach((job) => {
        const div = document.createElement("div");
        div.className = "match-box";
        div.innerHTML = `
          <h4>${job.title}</h4>
          <p><strong>Location:</strong> ${job.location}</p>
          <p><strong>Match:</strong> ${job.match}%</p>
          <a href="#">Apply</a>
        `;
        matchList.appendChild(div);
      });
    }
    updateResults(null, matchList);
  }

  function updateResults(jobList, matchList) {
    resultsDiv.innerHTML = "";
    const container = document.createElement("div");
    container.className = "result-container";

    const leftBox = document.createElement("div");
    leftBox.className = "left-box";
    const rightBox = document.createElement("div");
    rightBox.className = "right-box";

    if (jobList) leftBox.appendChild(jobList);
    if (matchList) rightBox.appendChild(matchList);

    container.appendChild(leftBox);
    container.appendChild(rightBox);
    resultsDiv.appendChild(container);
  }
});
