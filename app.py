@app.route('/revamp_cv', methods=['POST'])
def revamp_cv():
    original = request.form.get("cv_text", "")
    api_key = os.environ.get("OPENAI_API_KEY")
    print("🔍 OPENAI_API_KEY present:", bool(api_key))

    if not api_key:
        return render_template("cv_dr.html", revised="❌ OPENAI_API_KEY not set.", original=original)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
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
