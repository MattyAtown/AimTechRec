from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from datetime import datetime
import openai
import traceback  # for showing error tracebacks

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    cv_filename = db.Column(db.String(200), nullable=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

def get_recommended_jobs_for_user(user_id):
    return Job.query.limit(2).all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login_signup')
def login_signup():
    return render_template('login_signup.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/values')
def values():
    return render_template('values.html')

@app.route('/cv_dr', methods=['GET', 'POST'])
def cv_dr():
    if request.method == 'POST':
        file = request.files.get('cv_file')
        if file:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext not in app.config['ALLOWED_EXTENSIONS']:
                flash('Unsupported file type. Please upload a PDF or DOC/DOCX.', 'error')
                return redirect(url_for('cv_dr'))

            content = file.read().decode("utf-8", errors="ignore")
            feedback = {
                "positive": "✅ Clear formatting and structure.",
                "improvement": "🔧 Add metrics and stronger action verbs for impact."
            }
            combined_feedback = f"{feedback['positive']}\n\nSuggestions:\n{feedback['improvement']}"
            return render_template("cv_dr.html", feedback=combined_feedback, original=content)

    return render_template("cv_dr.html")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('login_signup'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for('dashboard'))
    flash("Invalid email or password.", "error")
    return redirect(url_for('login_signup'))

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already registered. Please log in.", "error")
        return redirect(url_for('login_signup'))
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('login_signup'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/live_jobs')
def live_jobs():
    jobs = Job.query.order_by(Job.date_posted.desc()).all()
    recommended = get_recommended_jobs_for_user(session.get('user_id'))
    return render_template('live_jobs.html', jobs=jobs, recommended=recommended)
@app.route('/revamp_cv', methods=['POST'])
def revamp_cv():
    original = request.form.get("cv_text", "")
    api_key = os.environ.get("OPENAI_API_KEY")
    print("✅ Using OpenAI Key:", api_key[:12] + "..." if api_key else "❌ None found")
    print("🔍 OPENAI_API_KEY present:", bool(api_key))

    if not api_key:
        return render_template("cv_dr.html", revised="❌ OPENAI_API_KEY not set.", original=original)

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional CV rewriting assistant. Enhance this CV for job search success."},
                {"role": "user", "content": f"Please rewrite and improve this CV:\n\n{original}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        revamped = response.choices[0].message.content
        return render_template("cv_dr.html", revised=revamped, original=original)
    except Exception as e:
        error_details = traceback.format_exc()
        return render_template("cv_dr.html", revised=f"❌ Full error:\n{error_details}", original=original)
from flask import request, jsonify

import requests
from flask import request, jsonify

@app.route('/api/live_jobs')
def get_live_jobs():
    title = request.args.get('title', '')
    location = request.args.get('location', '')
    min_salary = request.args.get('minSalary', '0')
    max_salary = request.args.get('maxSalary', '1000000')

    jobs = []

    # 1. JSearch API Integration
    try:
        query = f"{title} {location}"
        headers = {
            "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY", ""),
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": query,
            "num_pages": "1",
            "min_salary": min_salary,
            "max_salary": max_salary
        }
        response = requests.get("https://jsearch.p.rapidapi.com/search", headers=headers, params=params)
        data = response.json().get("data", [])
        for job in data:
            jobs.append({
                "title": job.get("job_title", "Unknown Role"),
                "location": job.get("job_city", "Unknown Location"),
                "salary": job.get("salary", "N/A"),
                "link": job.get("job_apply_link", "#"),
                "source": "JSearch"
            })
    except Exception as e:
        print("JSearch API Error:", e)

    # 2. Adzuna API Integration
    try:
        ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "9e85cf1e")
        ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "3c67192f4c294e0c5277762f4777f852")
        adzuna_url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1"
        adzuna_params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": 20,
            "what": title,
            "where": location,
            "salary_min": min_salary,
            "salary_max": max_salary,
            "content-type": "application/json"
        }
        adzuna_resp = requests.get(adzuna_url, params=adzuna_params)
        adzuna_data = adzuna_resp.json().get("results", [])
        for job in adzuna_data:
            jobs.append({
                "title": job.get("title", "N/A"),
                "location": job.get("location", {}).get("display_name", "N/A"),
                "salary": f"£{int(job.get('salary_min', 0))}/year" if job.get("salary_min") else "N/A",
                "link": job.get("redirect_url", "#"),
                "source": "Adzuna"
            })
    except Exception as e:
        print("Adzuna API Error:", e)

    return jsonify(jobs)


    import requests

    ADZUNA_APP_ID = '9e85cf1e'
    ADZUNA_APP_KEY = '3c67192f4c294e0c5277762f4777f852'

    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=20&what={title}&where={location}&salary_min={min_salary}&salary_max={max_salary}&content-type=application/json"

    response = requests.get(url)
    data = response.json()

    jobs = [
        {
            "title": job["title"],
            "location": job["location"]["display_name"],
            "salary": f"£{int(job.get('salary_min', 0))}/year" if job.get('salary_min') else "N/A",
            "description": job.get("description", "")
        }
        for job in data.get("results", [])
        if title.lower() in job["title"].lower()
    ]

    return jsonify(jobs)

    results = [
        job for job in filtered_jobs
        if title.lower() in job["title"].lower()
        and location.lower() in job["location"].lower()
        and work_type in job["work_type"]
        and industry in job["industry"]
    ]
    
    return jsonify(results)


@app.route('/api/smart_matches')
def get_smart_matches():
    if 'user_id' not in session:
        return jsonify([])

    user = User.query.get(session['user_id'])
    if not user or not user.cv_filename:
        return jsonify([])

    # Load and read the user's uploaded CV
    try:
        cv_path = os.path.join(app.config['UPLOAD_FOLDER'], user.cv_filename)
        with open(cv_path, 'r', encoding='utf-8', errors='ignore') as f:
            cv_text = f.read()
    except Exception as e:
        print("CV read error:", e)
        return jsonify([])

    keywords = [word.lower() for word in cv_text.split() if len(word) > 4][:10]
    query = ' '.join(keywords[:5])  # limit to 5 keywords to keep query clean

    # Call JSearch API
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": query,
            "num_pages": "1"
        }

        response = requests.get(url, headers=headers, params=params)
        results = response.json().get("data", [])

        def score(job):
            match_count = sum(1 for word in keywords if word in job.get("job_description", "").lower())
            return int((match_count / len(keywords)) * 100)

        matches = []
        for job in results:
            match_score = score(job)
            if match_score >= 50:
                matches.append({
                    "title": job.get("job_title", "Unknown"),
                    "location": job.get("job_city", "N/A"),
                    "salary": job.get("salary", "N/A"),
                    "skill_match": match_score,
                    "interview_prob": 70 + (match_score // 5),
                    "suitability": match_score
                })

        return jsonify(matches[:5])  # return top 5 smart matches
    except Exception as e:
        print("Smart Match Error:", e)
        return jsonify([])

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cv' not in request.files:
        return "No file part", 400
    file = request.files['cv']
    if file.filename == '':
        return "No selected file", 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({"message": "CV uploaded successfully", "filename": filename})

@app.route('/api/smart_match_v2')
def smart_match_v2():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user or not user.cv_filename:
        return jsonify({"error": "No CV found"}), 404

    try:
        # Load CV text
        cv_path = os.path.join(app.config['UPLOAD_FOLDER'], user.cv_filename)
        with open(cv_path, 'r', encoding='utf-8', errors='ignore') as f:
            cv_text = f.read()

        keywords = [word.lower() for word in cv_text.split() if len(word) > 4]
        top_keywords = keywords[:15]  # Only use top 15 words to reduce noise

        matches = []
        jobs = Job.query.order_by(Job.date_posted.desc()).all()

        for job in jobs:
            job_score = 0
            reasons = []

            # Title match
            if any(k in job.title.lower() for k in top_keywords):
                job_score += 20
                reasons.append("Title match")

            # Location match
            if any(k in (job.location or '').lower() for k in top_keywords):
                job_score += 10
                reasons.append("Location match")

            # Description match
            desc = job.__dict__.get("description", "").lower()
            matched_keywords = [k for k in top_keywords if k in desc]
            job_score += len(matched_keywords) * 3
            if matched_keywords:
                reasons.append(f"{len(matched_keywords)} keyword(s) matched")

            if job_score >= 40:
                matches.append({
                    "title": job.title,
                    "location": job.location,
                    "salary": job.salary or "N/A",
                    "score": f"{min(job_score, 100)}%",
                    "reasons": reasons
                })

        return jsonify(sorted(matches, key=lambda x: int(x['score'].replace('%', '')), reverse=True)[:10])

    except Exception as e:
        print("Smart match error:", e)
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
