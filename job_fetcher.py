import requests
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
DB_NAME = 'jobs.db'
ADZUNA_APP_ID = '9e85cf1e'
ADZUNA_APP_KEY = '3c67192f4c294e0c5277762f4777f852'

# Initialize the database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                created_at TEXT,
                source_id TEXT UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS archived_jobs AS SELECT * FROM jobs WHERE 0
        ''')
        conn.commit()

# Fetch live jobs from Adzuna API
def fetch_jobs():
    print("Fetching jobs from Adzuna...")
    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "sort_by": "date",
        "what": "developer OR engineer OR analyst",
        "content-type": "application/json"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            for job in data.get("results", []):
                c.execute('''
                    INSERT OR IGNORE INTO jobs (title, company, location, description, created_at, source_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    job.get("title"),
                    job.get("company", {}).get("display_name"),
                    job.get("location", {}).get("display_name"),
                    job.get("description"),
                    datetime.utcnow().isoformat(),
                    job.get("id")
                ))
            conn.commit()

# Archive jobs older than 30 days
def archive_old_jobs():
    print("Archiving jobs older than 30 days...")
    threshold_date = datetime.utcnow() - timedelta(days=30)
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO archived_jobs SELECT * FROM jobs WHERE datetime(created_at) < ?
        ''', (threshold_date.isoformat(),))
        c.execute('''
            DELETE FROM jobs WHERE datetime(created_at) < ?
        ''', (threshold_date.isoformat(),))
        conn.commit()

@app.route('/api/jobs')
def get_jobs():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT title, company, location, description, created_at FROM jobs ORDER BY datetime(created_at) DESC')
        jobs = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
        return jsonify(jobs)

@app.route('/api/archive')
def get_archived_jobs():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT title, company, location, description, created_at FROM archived_jobs ORDER BY datetime(created_at) DESC')
        jobs = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
        return jsonify(jobs)

if __name__ == '__main__':
    init_db()
    fetch_jobs()
    archive_old_jobs()

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_jobs, 'interval', hours=12)
    scheduler.add_job(archive_old_jobs, 'interval', hours=12)
    scheduler.start()

    app.run(debug=True)
