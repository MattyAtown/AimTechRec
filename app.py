from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
