from flask import Flask

# configure application
app = Flask(__name__)

@app.route("/")
def index():
    return "hello, world"
