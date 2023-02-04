from flask import Blueprint, render_template, url_for, request

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("index.html")