document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('search-btn');
    const titleInput = document.getElementById('job-title');
    const locationInput = document.getElementById('job-location');
    const jobResults = document.getElementById('job-results');
    const uploadBtn = document.getElementById('upload-btn');
    const cvInput = document.getElementById('cv-input');
    const cvPreview = document.getElementById('cv-preview');
    const matchedJobsContainer = document.getElementById('matched-jobs');

    let cvText = '';

    async function fetchJobs() {
        const title = titleInput.value;
        const location = locationInput.value;

        const res = await fetch(`/api/jobs?title=${encodeURIComponent(title)}&location=${encodeURIComponent(location)}`);
        const jobs = await res.json();

        jobResults.innerHTML = '';
        if (jobs.length === 0) {
            jobResults.innerHTML = '<p>No matching jobs found.</p>';
        } else {
            jobs.forEach(job => {
                const jobCard = document.createElement('div');
                jobCard.classList.add('job-card');
                jobCard.innerHTML = `
                    <h3>${job.title}</h3>
                    <p><strong>Company:</strong> ${job.company}</p>
                    <p><strong>Location:</strong> ${job.location}</p>
                    <p><strong>Salary:</strong> £${job.salary_min || 'N/A'}</p>
                    <p>${job.description.slice(0, 200)}...</p>
                `;
                jobResults.appendChild(jobCard);
            });
        }
    }

    async function uploadCV() {
        const file = cvInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('cv', file);

        const res = await fetch('/upload_cv', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        cvText = data.text;
        cvPreview.textContent = cvText.slice(0, 1000);

        fetchMatchedJobs();
    }

    async function fetchMatchedJobs() {
        if (!cvText) return;

        const res = await fetch('/api/match_cv_jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cv_text: cvText })
        });

        const matches = await res.json();
        matchedJobsContainer.innerHTML = '';

        if (matches.length === 0) {
            matchedJobsContainer.innerHTML = '<p>No strong matches found.</p>';
        } else {
            matches.forEach(job => {
                const matchCard = document.createElement('div');
                matchCard.classList.add('match-card');
                matchCard.innerHTML = `
                    <h3>${job.title} - ${job.location}</h3>
                    <p><strong>Match Score:</strong> ${job.match}</p>
                    <p><strong>Reasons:</strong> ${job.reasons.join(', ')}</p>
                `;
                matchedJobsContainer.appendChild(matchCard);
            });
        }
    }

    searchBtn.addEventListener('click', fetchJobs);
    uploadBtn.addEventListener('click', uploadCV);
});
