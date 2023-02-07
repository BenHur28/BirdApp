from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import current_user
from .models import Tweets, User
from . import db
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        text_content = request.form.get('tweet-text')
        new_tweet = Tweets(content=text_content,
                           user_id=current_user.id)
        db.session.add(new_tweet)
        db.session.commit()

    return render_template("index.html", current_user=current_user)


@views.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def view_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_user.follow(user)
        db.session.commit()
    return render_template("profile.html", current_user=user)
