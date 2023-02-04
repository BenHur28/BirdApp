from flask import Blueprint, render_template, url_for, request

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/logout')
def logout():
    pass


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(f"{request.form.get('email')}")
        print(f"{request.form.get('password')}")
        return url_for('views.home')
    return render_template("signup.html")

