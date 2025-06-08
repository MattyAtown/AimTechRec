

// === Job Card Click Handling for Pop-Up ===
function createModal(job) {
  const modal = document.createElement("div");
  modal.className = "job-modal";
  modal.innerHTML = `
    <div class="job-modal-content">
      <span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span>
      <h3>${job.title}</h3>
      <p><strong>Company:</strong> ${job.company || "N/A"}</p>
      <p><strong>Location:</strong> ${job.location}</p>
      <p><strong>Salary:</strong> £${job.salary || "Not listed"}</p>
      <p><strong>Description:</strong> ${job.description.slice(0, 500)}...</p>
      <label><input type="checkbox" id="shortlistConsent"> Yes, I’d like to be shortlisted</label>
      <button onclick="submitShortlist('${job.title}', '${job.location}', '${job.company || "N/A"}')">Submit</button>
    </div>`;
  document.body.appendChild(modal);
}

function submitShortlist(title, location, company) {
  const consent = document.getElementById("shortlistConsent").checked;
  if (!consent) {
    alert("Please tick the box to confirm you want to be shortlisted.");
    return;
  }
  fetch('/shortlist', {
    method: 'POST',
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, location, company })
  })
  .then(res => res.json())
  .then(data => {
    alert("✅ Your CV has been sent to our team.");
    document.querySelector(".job-modal")?.remove();
  })
  .catch(err => alert("Something went wrong. Please try again."));
}

// Attach event delegation for job cards (Live + Matched)
document.addEventListener("click", function(e) {
  if (e.target.closest(".job-box")) {
    const box = e.target.closest(".job-box");
    const job = {
      title: box.querySelector("h4").textContent,
      company: box.dataset.company,
      location: box.dataset.location,
      salary: box.dataset.salary,
      description: box.dataset.description
    };
    createModal(job);
  }
});
