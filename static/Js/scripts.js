document.addEventListener('DOMContentLoaded', function () {
  const searchButton = document.getElementById('search-jobs');
  const matchButton = document.getElementById('match-jobs');
  const jobResultsContainer = document.getElementById('job-results');
  const matchedJobsContainer = document.getElementById('matched-jobs');

  // Job Search via Adzuna API
  if (searchButton) {
    searchButton.addEventListener('click', async () => {
      const title = document.getElementById('job-title').value;
      const location = document.getElementById('job-location').value;

      jobResultsContainer.innerHTML = '<p>Loading jobs...</p>';

      try {
        const response = await fetch(`/api/jobs?title=${title}&location=${location}`);
        const jobs = await response.json();

        if (jobs.length === 0) {
          jobResultsContainer.innerHTML = '<p>No jobs found. Try adjusting filters.</p>';
        } else {
          jobResultsContainer.innerHTML = jobs.map(job => `
            <div class="job-card">
              <h3>${job.title}</h3>
              <p><strong>Company:</strong> ${job.company || "Unknown"}</p>
              <p><strong>Location:</strong> ${job.location}</p>
              <p><strong>Salary:</strong> ${job.salary_min || "Not listed"}</p>
              <p>${job.description.slice(0, 250)}...</p>
            </div>
          `).join('');
        }
      } catch (error) {
        jobResultsContainer.innerHTML = '<p>Error fetching jobs.</p>';
        console.error(error);
      }
    });
  }

  // Match CV against Jobs (dummy jobs + OpenAI)
  if (matchButton) {
    matchButton.addEventListener('click', async () => {
      matchedJobsContainer.innerHTML = '<p>Matching CV to jobs...</p>';

      try {
        const response = await fetch('/api/match_cv_jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cv_text: 'use_stored' }) // triggers backend use of stored CV
        });

        const matches = await response.json();

        if (matches.length === 0) {
          matchedJobsContainer.innerHTML = '<p>No matched jobs found.</p>';
        } else {
          matchedJobsContainer.innerHTML = matches.map(match => `
            <div class="job-card">
              <h3>${match.title} (${match.match}%)</h3>
              <p><strong>Location:</strong> ${match.location}</p>
              <p><strong>Top Match Reasons:</strong></p>
              <ul>${match.reasons.map(reason => `<li>${reason}</li>`).join('')}</ul>
            </div>
          `).join('');
        }
      } catch (error) {
        matchedJobsContainer.innerHTML = '<p>Error matching CV to jobs.</p>';
        console.error(error);
      }
    });
  }
});
