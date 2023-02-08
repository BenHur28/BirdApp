from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import current_user
from .models import Tweets, User, Replies
from . import db

import random
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':

        text_content = request.form.get('tweet-text')
        image_src = request.form.get('image_src')
        new_tweet = Tweets(content=text_content,
                           user_id=current_user.id,
                           image_src=image_src)
        db.session.add(new_tweet)
        db.session.commit()

    users = []
    for x in range(1,5):
        user = random.choice(User.query.all())
        if user not in users and user != current_user and not current_user.is_following(user):
            users.append(user)

    return render_template("index.html", current_user=current_user, users=users)


@views.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def view_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_user.follow(user)
        db.session.commit()
    return render_template("profile.html", user=user)


@views.route('/profile/<int:user_id>', methods=['POST'])
def follow_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_user.follow(user)
        db.session.commit()
        return redirect(url_for('view_profile', user=user))


@views.route('/reply/<int:tweet_id>', methods=['GET', 'POST'])
def reply(tweet_id):
    tweet = Tweets.query.get(tweet_id)
    if request.method == 'POST':
        text_content = request.form.get('reply-text')
        new_reply = Replies(content=text_content,
                            reply_author=current_user,
                            parent_tweet=tweet)
        db.session.add(new_reply)
        db.session.commit()
        return render_template("tweet.html", current_user=current_user, tweet=tweet)
    return render_template("tweet.html", current_user=current_user, tweet=tweet)