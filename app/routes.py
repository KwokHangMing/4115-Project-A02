from datetime import datetime
from flask import abort, render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from google.cloud import storage
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, SellForm, AdminForm
from app.models import User, Post, Category, Listing, ListingImage, Location, Ad
from app.email import send_password_reset_email
import os
from werkzeug.utils import secure_filename



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    listings = Listing.query.all()
    listings_images = ListingImage.query.all()
    location = Location.query.all()
    category = Category.query.all()
    storage_client = storage.Client.from_service_account_json(
        app.config['CRED_JSON'])
    bucket = storage_client.get_bucket(app.config['BUCKET_NAME'])
    blobs = list(bucket.list_blobs())
    latest_blob = sorted(blobs, key=lambda x: x.time_created, reverse=True)[0]
    latest_image_url = latest_blob.public_url
    # latest_image_url = get_latest_image_url()
    return render_template('index.html.j2', title=_('Carousell Hong Kong | Buy & Sell Cars, Property, Goods & Services'), listings=listings, listings_images=listings_images,
                           location=location, category=category, image_url=latest_image_url
                           )


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html.j2', title=_('Register'), form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('user.html.j2', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title=_('Edit Profile'),
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))

# our code here


@app.route('/electronics')
def electronics():
    return render_template('electronics.html.j2', title=_('Electronics'))


@app.route('/fashion')
def fashion():
    return render_template('fashion.html.j2', title=_('Fashion'))


@app.route('/luxury')
def luxury():
    return render_template('luxury.html.j2', title=_('Luxury'))


@app.route('/services')
def services():
    return render_template('services.html.j2', title=_('Services'))


@app.route('/cars')
def cars():
    return render_template('cars.html.j2', title=_('Cars'))


@app.route('/property')
def property():
    return render_template('property.html.j2', title=_('Properity'))


@app.route('/all_categories')
def all_categories():
    return render_template('all_categories.html.j2', title=_('All Categories'))


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    form = SellForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        # Create a GCS client
        storage_client = storage.Client.from_service_account_json(
            app.config['CRED_JSON'])
        bucket = storage_client.bucket(app.config['BUCKET_NAME'])
        # Set the blob name or path of the file to upload
        blob = bucket.blob(f'images/{filename}')
        # Upload the file to the blob
        blob.upload_from_string(
            image_file.read(), content_type=image_file.content_type)
        # Create the ListingImage object with the filename
        image = ListingImage(path=f'images/{filename}')
        # Get the category object based on the selected category name
        category = Category(name=form.category.data)
        # Create the Listing object with the form data, user and category objects
        listing = Listing(title=form.title.data,
                          description=form.description.data,
                          price=form.price.data,
                          status='available',  # set the status to 'available'
                          user=current_user,
                          category=category)
        # Add the objects to the database
        location_name = Location(name=form.location.name)
        db.session.add(category)
        db.session.add(image)
        db.session.add(listing)
        db.session.add(location_name)
        db.session.commit()
        flash(_('Your item has been saved.'))
        return redirect(url_for('index'))
    return render_template('sell.html.j2', title=_('Sell or Give Away Items, Offer Services, or Rent Out Your Apartment on Carousell'), form=form)

# This is useless.


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        title = form.title.data
        image_url = form.image_url.data
        ad = Ad(title=title, image_url=image_url)
        db.session.add(ad)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('admin.html.j2', title=_('Admin'), form=form)
# -----------------------------------------------------------------------


@app.route('/product_details/<int:id>', methods=['GET', 'POST'])
def product_details(id):
    listing = Listing.query.get(id)
    return render_template('product_details.html.j2', listing=listing, id=id)
