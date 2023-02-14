from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import current_user
from .models import *
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
                           image_src=image_src,
                           original_author=current_user.username,
                           original_author_id=current_user.id,)
        db.session.add(new_tweet)
        db.session.commit()

    users = []
    for x in range(1, 5):
        user = random.choice(User.query.all())
        if (user not in users) and (user != current_user) and (not current_user.is_following(user)):
            users.append(user)
    list_of_tweets = []
    for tweet in current_user.followed_posts():
        list_of_tweets.insert(0, tweet)
    return render_template("index.html", current_user=current_user, users=users, tweets=list_of_tweets)


@views.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def view_profile(user_id):
    user_query = User.query.get(user_id)
    list_of_tweets = []
    users = []
    print("hello")
    for x in range(1, 5):
        user = random.choice(User.query.all())
        if (user not in users) and (user != current_user) and (not current_user.is_following(user)):
            users.append(user)
    for tweet in user_query.tweets:
        list_of_tweets.insert(0, tweet)
    if request.method == 'POST':
        current_user.follow(user_query)
        db.session.commit()
    return render_template("profile.html", user=user_query, users=users, tweets=list_of_tweets)


@views.route('/follow/<int:user_id>', methods=['POST'])
def follow_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_user.follow(user)
        db.session.commit()
        return redirect(url_for('views.home'))


@views.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_user.unfollow(user)
        db.session.commit()
        return redirect(url_for('views.home'))


@views.route('/tweet/<int:tweet_id>', methods=['GET', 'POST'])
def view_tweet(tweet_id):
    tweet = Tweets.query.get(tweet_id)
    users = []
    for x in range(1, 5):
        user = random.choice(User.query.all())
        if (user not in users) and (user != current_user) and (not current_user.is_following(user)):
            users.append(user)
    if request.method == 'POST':
        text_content = request.form.get('reply-text')
        image_src = request.form.get('image_src')
        new_reply = Replies(content=text_content,
                            reply_author=current_user,
                            image_src=image_src,
                            parent_tweet=tweet,
                            parent=None,
                            original_author=current_user.username,
                            original_author_id=current_user.id)
        db.session.add(new_reply)
        db.session.commit()
    return render_template("tweet.html", users=users, current_user=current_user, tweet=tweet)


@views.route('/replies/<int:reply_id>', methods=['GET', 'POST'])
def reply_to_reply(reply_id):
    main_reply = Replies.query.get(reply_id)
    print(main_reply.replies.count())
    if request.method == 'POST':
        text_content = request.form.get('reply-text')
        image_src = request.form.get('image_src')
        new_reply = Replies(content=text_content,
                            reply_author=current_user,
                            image_src=image_src,
                            parent_tweet=None,
                            parent=main_reply,
                            original_author=current_user.username,
                            original_author_id=current_user.id)
        db.session.add(new_reply)
        db.session.commit()
        return redirect(url_for('views.reply_to_reply', reply_id=reply_id))
    return render_template("reply.html", main_reply=main_reply, current_user=current_user)


@views.route('/profile/<int:user_id>/following')
def view_following(user_id):
    user = User.query.get(user_id)
    list_of_following = []
    for following_user in user.followed:
        f_user = User.query.get(following_user.id)
        list_of_following.append(f_user)
    return render_template("following.html", followings=list_of_following)


@views.route('/profile/<int:user_id>/followers')
def view_followers(user_id):
    user = User.query.get(user_id)
    list_of_followers = []
    for follower_user in user.following:
        f_user = User.query.get(follower_user.id)
        list_of_followers.append(f_user)
    return render_template("followers.html", followers=list_of_followers)


@views.route('/delete_tweet/<int:tweet_id>')
def delete_tweet(tweet_id):
    tweet_to_delete = Tweets.query.get(tweet_id)
    db.session.delete(tweet_to_delete)
    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/delete_retweet/<int:tweet_id>')
def delete_retweet(tweet_id):
    tweet_to_delete = Tweets.query.get(tweet_id)
    if not tweet_to_delete.is_quote_retweet:
        if tweet_to_delete.from_reply:
            reply_to_un_retweet = Replies.query.get(tweet_to_delete.original_id)
            reply_to_un_retweet.un_retweet(current_user)
            db.session.query(Replies).filter(Replies.id == tweet_to_delete.original_id).update({'retweet_count': Replies.retweet_count - 1})
        else:
            tweet_to_un_retweet = Tweets.query.get(tweet_to_delete.original_id)
            tweet_to_un_retweet.un_retweet(current_user)
            db.session.query(Tweets).filter(Tweets.id == tweet_to_delete.original_id).update({'retweet_count': Tweets.retweet_count - 1})
    elif tweet_to_delete.is_quote_retweet:
        if tweet_to_delete.from_reply:
            reply_to_un_retweet = Replies.query.get(tweet_to_delete.parent_id)
            reply_to_un_retweet.un_retweet(current_user)
            db.session.query(Replies).filter(Replies.id == tweet_to_delete.parent_id).update({'retweet_count': Replies.retweet_count - 1})
        else:
            tweet_to_un_retweet = Tweets.query.get(tweet_to_delete.parent_id)
            tweet_to_un_retweet.un_retweet(current_user)
            db.session.query(Tweets).filter(Tweets.id == tweet_to_delete.parent_id).update({'retweet_count': Tweets.retweet_count - 1})
    db.session.delete(tweet_to_delete)
    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/delete_reply/<int:reply_id>')
def delete_reply(reply_id):
    reply_to_delete = Replies.query.get(reply_id)
    db.session.delete(reply_to_delete)
    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/like_tweet/<int:tweet_id>')
def like_tweet(tweet_id):
    tweet = Tweets.query.get(tweet_id)
    tweet.like(current_user)
    db.session.commit()
    return redirect(url_for('views.view_tweet', tweet_id=tweet_id))


@views.route('/unlike_tweet/<int:tweet_id>')
def unlike_tweet(tweet_id):
    tweet = Tweets.query.get(tweet_id)
    tweet.unlike(current_user)
    db.session.commit()
    return redirect(url_for('views.view_tweet', tweet_id=tweet_id))


@views.route('/like_reply/<int:reply_id>')
def like_reply(reply_id):
    reply = Replies.query.get(reply_id)
    reply.like(current_user)
    db.session.commit()
    return redirect(url_for('views.reply_to_reply', reply_id=reply_id))


@views.route('/unlike_reply/<int:reply_id>')
def unlike_reply(reply_id):
    reply = Replies.query.get(reply_id)
    reply.unlike(current_user)
    db.session.commit()
    return redirect(url_for('views.reply_to_reply', reply_id=reply_id))


@views.route('/quote_retweet_tweet/<int:tweet_id>')
def quote_retweet_tweet(tweet_id):
    tweet = Tweets.query.get(tweet_id)
    if tweet.original_id is None:
        db.session.query(Tweets).filter(Tweets.id == tweet_id).update({'original_id': tweet.id})
        db.session.commit()
    new_tweet = Tweets(content=tweet.content,
                       user_id=current_user.id,
                       image_src=tweet.image_src,
                       is_retweet=True,
                       is_quote_retweet=True,
                       original_author=tweet.original_author,
                       original_author_id=tweet.original_author_id,
                       original_id=tweet.original_id,
                       parent_id=tweet_id)
    db.session.add(new_tweet)
    if not tweet.is_retweet:
        db.session.query(Tweets).filter(Tweets.id == tweet.original_id).update({'retweet_count': Tweets.retweet_count + 1})
    else:
        db.session.query(Tweets).filter(Tweets.id == tweet_id).update({'retweet_count': Tweets.retweet_count + 1})
    tweet.retweet(current_user)
    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/quote_retweet_reply/<int:reply_id>')
def quote_retweet_reply(reply_id):
    reply = Replies.query.get(reply_id)
    if reply.original_id is None:
        db.session.query(Replies).filter(Replies.id == reply_id).update({'original_id': reply.id})
        db.session.commit()
    new_tweet = Tweets(content=reply.content,
                       user_id=current_user.id,
                       image_src=reply.image_src,
                       is_retweet=True,
                       is_quote_retweet=True,
                       from_reply=True,
                       original_author=reply.original_author,
                       original_author_id=reply.original_author_id,
                       original_id=reply.original_id,
                       parent_id=reply_id)
    db.session.add(new_tweet)
    if not reply.is_retweet:
        db.session.query(Replies).filter(Replies.id == reply.original_id).update({'retweet_count': Replies.retweet_count + 1})
    else:
        db.session.query(Replies).filter(Replies.id == reply_id).update({'retweet_count': Replies.retweet_count + 1})
    reply.retweet(current_user)
    db.session.commit()
    return redirect(url_for('views.home'))
