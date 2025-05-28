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
