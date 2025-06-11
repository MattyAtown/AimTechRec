
from docx import Document
from openai import OpenAI
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
import requests
import os
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "e8c3b90a9d5c407c9e12311cfec4cdbc"
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aimtechrec.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "uploads"

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
client = OpenAI(api_key=OPENAI_API_KEY)

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

@app.route('/cv_dr', methods=["GET"])
def cv_dr():
    user = User.query.filter_by(name=session.get("user", "default_user")).first()
    return render_template("cv_dr.html", user=user)

@app.route("/revamp_cv", methods=["POST"])
def revamp_cv():
    original_text = request.form.get("cv_text", "")
    try:
        response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a professional CV writer."},
        {
            "role": "user",
            "content": f"""Please improve this CV:

{original_text}"""
        }
    ]
)
        revised = response.choices[0].message.content
    except Exception as e:
        revised = f"⚠️ Error improving CV: {str(e)}"
    user = User.query.filter_by(name=session.get("user", "default_user")).first()
    return render_template("cv_dr.html", revised=revised, original=original_text, user=user)

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
            return jsonify({"text": text})
    return jsonify({"error": "Upload failed"})

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

@app.route('/services')
def services():
    return render_template('services.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
