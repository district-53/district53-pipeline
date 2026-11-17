from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
@app.route("/signup/<role>")
def signup(role="commonfolk"):
    return render_template("signup.html", role=role)

@app.route("/book")
def book():
    return render_template("book.html")

if __name__ == "__main__":
    app.run(debug=True)