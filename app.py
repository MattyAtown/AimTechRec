from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/values")
def values():
    return render_template("values.html")

@app.route("/static/<path:path>")
def static_files(path):
    return app.send_static_file(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
