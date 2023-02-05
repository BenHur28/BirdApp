from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('views.home'))
            else:
                print("Incorrect Password")
                return redirect(url_for('auth.login'))
        else:
            print("Email does not exist.")
            return redirect(url_for('auth.login'))
    return render_template("login.html", current_user=current_user)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hash_and_salted_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256',
                                                          salt_length=8)
        new_user = User(email=request.form.get('email'),
                        password=hash_and_salted_password,
                        username=request.form.get('username'))

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('views.home'))
    return render_template("signup.html", current_user=current_user)
