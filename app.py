from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import secrets
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message

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

@app.route('/live_jobs')
def live_jobs():
    return render_template('live_jobs.html')

@app.route('/cv_dr')
def cv_dr():
    return render_template('cv_dr.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('login_signup'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'user_id' not in session:
        flash('Please log in to upload your CV.', 'error')
        return redirect(url_for('login_signup'))
    file = request.files.get('cv')
    if file and file.filename.split('.')[-1].lower() in app.config['ALLOWED_EXTENSIONS']:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user = User.query.get(session['user_id'])
        user.cv_filename = filename
        db.session.commit()
        flash('CV uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Please upload a PDF, DOC, or DOCX.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/send_verification/<email>')
def send_verification(email):
    user = User.query.filter_by(email=email).first()
    if user and not user.verified:
        token = serializer.dumps(email, salt='email-confirm')
        verification_link = url_for('verify_email', token=token, _external=True)
        msg = Message('Verify Your Email', recipients=[email])
        msg.body = f"Hi {user.name},\n\nPlease click the link below to verify your email:\n{verification_link}\n\nThank you for joining AiM Technology!"
        mail.send(msg)
        flash('Verification email sent. Please check your inbox.', 'success')
    return redirect(url_for('login_signup'))

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('login_signup'))
    except SignatureExpired:
        flash('The verification link has expired. Please try again.', 'error')
        return redirect(url_for('login_signup'))
    flash('Invalid verification link.', 'error')
    return redirect(url_for('login_signup'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
