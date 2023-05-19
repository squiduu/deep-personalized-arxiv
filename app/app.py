from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_restx import Api, Resource
from user import User
from papers import Papers
from utils import token_required

app = Flask(__name__, template_folder='./templates')
api = Api(app)

api.add_namespace(User, path='/api/v1/users')
api.add_namespace(Papers, path='/api/v1/papers')


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@app.route('/main', methods=['GET'])
@token_required
def main_page():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
