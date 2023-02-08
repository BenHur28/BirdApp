from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100))

    tweets = relationship("Tweets", back_populates="tweet_author")

    replies = relationship("Replies", back_populates="reply_author")

    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Tweets.query.join(
            followers, (followers.c.followed_id == Tweets.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Tweets.query.filter_by(user_id=self.id)
        return followed.union(own)


class Tweets(db.Model):
    __tablename__ = "tweets"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))
    likes = db.Column(db.Integer)
    retweets = db.Column(db.Integer)
    image_src = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tweet_author = relationship("User", back_populates="tweets")

    replies = relationship("Replies", back_populates="parent_tweet")


class Replies(db.Model):
    __tablename__ = "replies"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tweet_id = db.Column(db.Integer, db.ForeignKey("tweets.id"))

    reply_author = relationship("User", back_populates="replies")
    parent_tweet = relationship("Tweets", back_populates="replies")