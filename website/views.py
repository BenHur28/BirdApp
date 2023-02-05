from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import current_user
from .models import Tweets
from . import db
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        text_content = request.form.get('tweet-text')
        new_tweet = Tweets(content=text_content)
        db.session.add(new_tweet)
        db.session.commit()

    return render_template("index.html", current_user=current_user)



