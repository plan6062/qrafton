from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return render_template('index.html', title="Hello World")

if __name__ == '__main__':
    app.run(debug=True)