"""
qbrack web page v.0.1
"""
from flask import Flask
from controllers.app_controller import AppController

app = Flask(__name__)
AppController(app)

if __name__ == "__main__":
    app.run(debug=True)
