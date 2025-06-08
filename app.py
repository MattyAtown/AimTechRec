from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
import requests
import os
import fitz  # PyMuPDF
import openai
from PyPDF2 import PdfReader
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "e8c3b90a9d5c407c9e12311cfec4cdbc"
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aimtechrec.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    cv_text = db.Column(db.Text)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/live_jobs')
def live_jobs():
    return render_template("live_jobs.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        session["user"] = user.name
        flash(f"👋 Welcome back, {user.name}!")
        return redirect(url_for("dashboard"))
    else:
        flash("❌ Invalid credentials, try again.")
        return redirect(url_for("login_signup"))

@app.route("/login_signup", methods=["GET"])
def login_signup():
    return render_template("login_signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already registered. Please log in.")
        return redirect(url_for("login_signup"))
    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    session["user"] = name
    flash(f"🎉 Welcome to AiM, {name}!")
    return redirect(url_for("dashboard"))

@app.route("/cv_dr", methods=["GET", "POST"])
def cv_dr():
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("login_signup"))
    user = User.query.filter_by(name=session["user"]).first()
    if request.method == "POST":
        uploaded_file = request.files.get("cv_file")
        if not uploaded_file:
            return render_template("cv_dr.html", user=user, feedback="❌ No file uploaded.")
        if uploaded_file.filename.endswith(".pdf"):
            try:
                reader = PdfReader(uploaded_file)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            except Exception as e:
                return render_template("cv_dr.html", user=user, feedback=f"❌ Failed to read PDF: {str(e)}")
        else:
            return render_template("cv_dr.html", user=user, feedback="❌ Unsupported file format. Please upload a PDF.")
        user.cv_text = text
        db.session.commit()
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a career expert reviewing CVs."},
                    {"role": "user", "content": f"Can you review this CV and give a short summary of its strengths and weaknesses:\n\n{text}"}
                ]
            )
            feedback = response.choices[0].message.content
        except Exception as e:
            feedback = f"⚠️ Error generating feedback: {str(e)}"
        return render_template("cv_dr.html", user=user, feedback=feedback, original=text)
    return render_template("cv_dr.html", user=user)

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("login_signup"))
    user = User.query.filter_by(name=session["user"]).first()
    return render_template("dashboard.html", user=user)

@app.route('/cv_storage_success')
def cv_storage_success():
    return render_template("cv_storage_success.html")

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    file = request.files['cv']
    if file and "user" in session:
        text = extract_text_from_pdf(file)
        user = User.query.filter_by(name=session["user"]).first()
        if user:
            user.cv_text = text
            db.session.commit()
            flash("📄 Your CV has been uploaded and saved.")
            return redirect(url_for('cv_storage_success'))
    flash("⚠️ Something went wrong. Try again.")
    return redirect(url_for('cv_dr'))

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
    user_cv = request.json.get("cv_text", '')
    if not user_cv:
        return jsonify([])
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
    session.pop("user", None)
    flash("👋 You've been logged out.")
    return redirect(url_for('login_signup'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/shortlist', methods=['POST'])
def shortlist():
    data = request.json
    title = data.get("title")
    location = data.get("location")
    company = data.get("company")
    print(f"Shortlist Request: {title} at {company} in {location}")
    return jsonify({"message": "Shortlist request received."})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
