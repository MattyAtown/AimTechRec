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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
