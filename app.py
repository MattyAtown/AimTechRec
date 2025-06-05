
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import requests
import os
import fitz  # PyMuPDF

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

@app.route('/live_jobs', methods=['GET'])
def live_jobs():
    global cv_text_store
    title = request.args.get('title', 'developer')
    location = request.args.get('location', 'london')

    jobs = []
    matched_jobs = []

    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=20&what={title}&where={location}&content-type=application/json"
    res = requests.get(url)

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

            # Match jobs using OpenAI if CV is uploaded
            if cv_text_store and OPENAI_API_KEY:
                match_score, reason = score_cv_openai(cv_text_store, job_data["description"])
                if match_score >= 50:  # Only include jobs with match score >= 50
                    job_data["match_score"] = match_score
                    job_data["reason"] = reason
                    matched_jobs.append(job_data)

        matched_jobs = sorted(matched_jobs, key=lambda x: x["match_score"], reverse=True)

    return render_template("live_jobs.html", jobs=jobs, matched_jobs=matched_jobs)

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    global cv_text_store
    file = request.files['cv']
    if file:
        text = extract_text_from_pdf(file)
        cv_text_store = text
        return jsonify({"text": text})
    return jsonify({"error": "No file uploaded"}), 400

def score_cv_openai(cv_text, job_description):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        prompt = f"Compare the following CV with this job description and give a score out of 100 with a short reason:

CV:
{cv_text[:2000]}

Job Description:
{job_description[:1000]}"
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers,
                                 json={
                                     "model": "gpt-4",
                                     "messages": [
                                         {"role": "system", "content": "You are a professional recruitment assistant."},
                                         {"role": "user", "content": prompt}
                                     ]
                                 })
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            import re
            match = re.search(r'(\d{1,3})', content)
            score = int(match.group(1)) if match else 0
            return min(score, 100), content.strip()
        else:
            return 0, "OpenAI Error"
    except Exception as e:
        return 0, f"Error: {str(e)}"

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    return text

@app.route('/cv_dr')
def cv_dr():
    return render_template("cv_dr.html")

@app.route('/login_signup')
def login_signup():
    return render_template("login_signup.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/cv_storage_success')
def cv_storage_success():
    return render_template("cv_storage_success.html")

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
