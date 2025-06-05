
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import requests
import os
import fitz  # PyMuPDF
import openai

app = Flask(__name__)
CORS(app)

# Environment variables
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# In-memory CV text (temporary storage)
cv_text_store = ""

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/live_jobs')
def live_jobs():
    global cv_text_store

    title = request.args.get('title', 'developer')
    location = request.args.get('location', 'london')

    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=10&what={title}&where={location}&content-type=application/json"
    res = requests.get(url)

    jobs = []
    matched_jobs = []

    if res.status_code == 200:
        results = res.json().get('results', [])
        for job in results:
            job_data = {
                "title": job.get("title", "N/A"),
                "location": job.get("location", {}).get("display_name", "N/A"),
                "salary": job.get("salary_min", "N/A"),
                "description": job.get("description", "")
            }
            jobs.append(job_data)

            if cv_text_store:
                match_score = score_cv_match(cv_text_store.lower(), job_data["description"].lower())
                if match_score > 0:
                    job_data["match_score"] = match_score
                    matched_jobs.append(job_data)

        matched_jobs = sorted(matched_jobs, key=lambda x: x["match_score"], reverse=True)

    return render_template("live_jobs.html", jobs=jobs, matched_jobs=matched_jobs)

@app.route('/login_signup')
def login_signup():
    return render_template("login_signup.html")

@app.route('/cv_dr')
def cv_dr():
    return render_template("cv_dr.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/cv_storage_success')
def cv_storage_success():
    return render_template("cv_storage_success.html")

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

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    return text

def score_cv_match(cv, job_description):
    keywords = [
        "software", "programming", "html", "css", "javascript",
        "angularjs", "python", "java", "oracle", "sql",
        "dba", "analyst", "architect", "director"
    ]
    return sum(1 for kw in keywords if kw in cv and kw in job_description)

@app.route('/services')
def services():
    return render_template("services.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/values')
def values():
    return render_template("values.html")

@app.route('/logout')
def logout():
    return redirect(url_for('login_signup'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
