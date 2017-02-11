from flask import Flask

# configure application
app = Flask(__name__)

@app.route("/")
def index():
    return "hello, world"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()