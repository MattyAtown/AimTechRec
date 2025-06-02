from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
import fitz  # PyMuPDF
import openai

app = Flask(__name__)
CORS(app)

# Environment variables for security
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# In-memory CV storage (for demo)
cv_text_store = ""

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/live_jobs')
def live_jobs():
    return render_template("live_jobs.html")

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    global cv_text_store
    file = request.files['cv']
    if file:
        text = extract_text_from_pdf(file)
        cv_text_store = text
        return jsonify({"text": text})
    return jsonify({"error": "No file uploaded"}), 400

@app.route('/api/jobs')
def search_jobs():
    title = request.args.get('title', '')
    location = request.args.get('location', 'london')

    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=10&what={title}&where={location}&content-type=application/json"
    res = requests.get(url)
    if res.status_code == 200:
        jobs = res.json().get('results', [])
        job_list = [{
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "salary_min": job.get("salary_min"),
            "description": job.get("description")
        } for job in jobs]
        return jsonify(job_list)
    return jsonify([])

@app.route('/api/match_cv_jobs', methods=['POST'])
def match_jobs():
    global cv_text_store
    user_cv = request.json.get("cv_text", '')
    if not user_cv:
        return jsonify([])

    # Example jobs to compare (would usually come from DB or Adzuna cache)
    dummy_jobs = [
        {"title": "Software Engineer", "location": "London", "description": "We are looking for a Python developer with Flask experience."},
        {"title": "Data Analyst", "location": "Manchester", "description": "Strong skills in SQL and data visualization."},
        {"title": "DevOps Engineer", "location": "Remote", "description": "Experience with CI/CD pipelines and AWS required."}
    ]

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    matches = []
    for job in dummy_jobs:
        prompt = f"Compare this CV:\n{user_cv[:2000]}\n\nWith this job description:\n{job['description']}\n\nHow strong is the match from 0-100? Give reasons."
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers,
                                 json={
                                     "model": "gpt-4",
                                     "messages": [
                                         {"role": "system", "content": "You are a CV-job matching assistant."},
                                         {"role": "user", "content": prompt}
                                     ]
                                 })
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            score = extract_score_from_response(content)
            reasons = extract_reasons(content)
            matches.append({
                "title": job['title'],
                "location": job['location'],
                "match": score,
                "reasons": reasons
            })
    return jsonify(matches)

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    return text

def extract_score_from_response(text):
    import re
    match = re.search(r'(\d{1,3})', text)
    if match:
        score = int(match.group(1))
        return min(score, 100)
    return 0

def extract_reasons(text):
    lines = text.split("\n")
    reasons = [line.strip("- ") for line in lines if "match" in line.lower() or "because" in line.lower()]
    return reasons[:3] if reasons else ["See description"]

if __name__ == '__main__':
    app.run(debug=True)
