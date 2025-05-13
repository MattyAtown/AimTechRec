import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login_signup')
def login_signup():
    return render_template('login_signup.html')

@app.route('/live_jobs')
def live_jobs():
    return render_template('live_jobs.html')

@app.route('/cv_dr')
def cv_dr():
    return render_template('cv_dr.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/values')
def values():
    return render_template('values.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port Render provides
    app.run(host="0.0.0.0", port=port, debug=True)
