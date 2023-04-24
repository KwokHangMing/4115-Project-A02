
from datetime import datetime, timedelta, timezone
from hashlib import md5
from app import app, db, login
import jwt
from flask_login import UserMixin, current_user

from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    listings = db.relationship(
        'Listing', back_populates='user')
    is_admin = db.Column(db.Boolean(), default=False)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, followers.c.followed_id == Post.user_id
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
        except:
            return None
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<Post {self.body}>'

# our code here(Leo)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    listings = db.relationship('Listing', back_populates="category")
    name = db.Column(db.String(255), nullable=False)

class Listing(db.Model):
    __tablename__ = 'listing'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='listings')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', back_populates='listings')
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='available')
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    location = db.Column(db.String(100), nullable=False)
    listingimage = db.relationship('ListingImage', uselist=False, back_populates='image')


class ListingImage(db.Model):
    __tablename__ = 'listing_image'
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey(
        'listing.id'), nullable=False)
    image = db.relationship('Listing', uselist=False, back_populates='listingimage')
    path = db.Column(db.String(100))


class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    image_url = db.Column(db.String(200))

# Alex coding here
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


listing_tags = db.Table('listing_tags',
                        db.Column('listing_id', db.Integer, db.ForeignKey(
                            'listing.id'), primary_key=True),
                        db.Column('tag_id', db.Integer, db.ForeignKey(
                            'tag.id'), primary_key=True)
                        )


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer = db.relationship('User', foreign_keys=[
                            buyer_id], backref=db.backref('reviews_given', lazy=True))
    seller = db.relationship('User', foreign_keys=[
                             seller_id], backref=db.backref('reviews_received', lazy=True))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.relationship('User', foreign_keys=[
                             sender_id], backref=db.backref('sent_messages', lazy=True))
    receiver = db.relationship('User', foreign_keys=[
                               receiver_id], backref=db.backref('received_messages', lazy=True))


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(
        'User', backref=db.backref('notifications', lazy=True))


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return f"Report('{self.message}')"
#(jonas)
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(50), nullable=False)
    card_number = db.Column(db.String(50), nullable=False)
    cvv = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Payment {self.id}>'
    

class UserLocations(db.Model):
    __tablename__ = 'User_Location'
    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<UserLocations {self.id}>'

