from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/service-catalogue.html")
def service_catalogue():
    return render_template("service-catalogue.html")

@app.route("/company-values.html")
def company_values():
    return render_template("company-values.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
