from flask import request, jsonify

@app.route('/api/live_jobs')
def get_live_jobs():
    title = request.args.get('title', '')
    location = request.args.get('location', '')
    min_salary = int(request.args.get('minSalary', 0))
    max_salary = int(request.args.get('maxSalary', 1_000_000))
    work_type = request.args.get('workType', '')
    industry = request.args.get('industry', '')

    # You can later replace this dummy list with real API data
    filtered_jobs = [
        {
            "title": "Technical Architect",
            "location": "London",
            "salary": "£700/day",
            "work_type": "hybrid",
            "industry": "tech"
        },
        {
            "title": "Cybersecurity Consultant",
            "location": "Remote",
            "salary": "£650/day",
            "work_type": "remote",
            "industry": "tech"
        }
    ]

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
    # In production: extract user CV keywords, calculate skill match with jobs
    ai_matches = [
        {
            "title": "Cloud Infrastructure Engineer",
            "location": "Manchester",
            "salary": "£600/day",
            "skill_match": 92,
            "interview_prob": 85,
            "suitability": 89
        },
        {
            "title": "DevSecOps Lead",
            "location": "Bristol",
            "salary": "£720/day",
            "skill_match": 88,
            "interview_prob": 80,
            "suitability": 84
        }
    ]
    return jsonify(ai_matches)
