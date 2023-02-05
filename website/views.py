from flask import Blueprint, render_template, url_for, request
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("index.html", current_user=current_user)