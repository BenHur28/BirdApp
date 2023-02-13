from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

followings = db.Table('followings',
                      db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('follower_id', db.Integer, db.ForeignKey('user.id'))
                      )

likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('tweet_id', db.Integer, db.ForeignKey('tweets.id'))
                 )

likes_reply = db.Table('likes_reply',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('reply_id', db.Integer, db.ForeignKey('replies.id'))
                       )

retweeted_tweet = db.Table('retweeted_tweet',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('tweet_id', db.Integer, db.ForeignKey('tweets.id'))
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

    following = db.relationship('User', secondary=followings,
                                primaryjoin=(followings.c.followed_id == id),
                                secondaryjoin=(followings.c.follower_id == id),
                                backref=db.backref('followings', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            user.following.append(self)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            user.following.remove(self)

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
    image_src = db.Column(db.String(255))
    is_retweet = db.Column(db.Boolean, default=False)
    is_quote_retweet = db.Column(db.Boolean, default=False)
    retweet_count = db.Column(db.Integer, default=0)
    original_author = db.Column(db.String(255))
    original_author_id = db.Column(db.Integer)
    original_id = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tweet_author = relationship("User", back_populates="tweets")
    replies = relationship("Replies", back_populates="parent_tweet", cascade="all, delete, delete-orphan")

    liked = db.relationship('User', secondary=likes,
                            primaryjoin=(likes.c.tweet_id == id),
                            secondaryjoin=(likes.c.user_id == User.id),
                            backref=db.backref('likes', lazy='dynamic'), lazy='dynamic')

    retweeted = db.relationship('User', secondary=retweeted_tweet,
                                primaryjoin=(retweeted_tweet.c.tweet_id == id),
                                secondaryjoin=(retweeted_tweet.c.user_id == User.id),
                                backref=db.backref('retweeted_tweet', lazy='dynamic'), lazy='dynamic')

    def like(self, user):
        if not self.is_liked(user):
            self.liked.append(user)

    def unlike(self, user):
        if self.is_liked(user):
            self.liked.remove(user)

    def is_liked(self, user):
        return self.liked.filter(likes.c.user_id == user.id).count() > 0

    def retweet(self, user):
        if not self.is_retweeted(user):
            self.retweeted.append(user)

    def un_retweet(self, user):
        if self.is_retweeted(user):
            self.retweeted.remove(user)

    def is_retweeted(self, user):
        return self.retweeted.filter(retweeted_tweet.c.user_id == user.id).count() > 0


class Replies(db.Model):
    __tablename__ = "replies"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))
    image_src = db.Column(db.String(255))
    is_retweet = db.Column(db.Boolean, default=False)
    is_quote_retweet = db.Column(db.Boolean, default=False)
    retweet_count = db.Column(db.Integer, default=0)
    original_author = db.Column(db.String(255))
    original_author_id = db.Column(db.Integer)
    original_id = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tweet_id = db.Column(db.Integer, db.ForeignKey("tweets.id"))

    reply_author = relationship("User", back_populates="replies")
    parent_tweet = relationship("Tweets", back_populates="replies")

    parent_id = db.Column(db.Integer, db.ForeignKey('replies.id'))
    replies = db.relationship("Replies", backref=db.backref('parent', remote_side=[id]), lazy='dynamic',
                              cascade="all, delete, delete-orphan")

    liked = db.relationship('User', secondary=likes_reply,
                            primaryjoin=(likes_reply.c.reply_id == id),
                            secondaryjoin=(likes_reply.c.user_id == User.id),
                            backref=db.backref('likes_reply', lazy='dynamic'), lazy='dynamic')

    def like(self, user):
        if not self.is_liked(user):
            self.liked.append(user)

    def unlike(self, user):
        if self.is_liked(user):
            self.liked.remove(user)

    def is_liked(self, user):
        return self.liked.filter(likes_reply.c.user_id == user.id).count() > 0
