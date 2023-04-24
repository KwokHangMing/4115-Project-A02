from datetime import datetime
from flask import abort, jsonify, render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from google.cloud import storage

from app import app, db, admin_required
from app.forms import *
from app.models import *
from app.email import send_password_reset_email
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
    storage_client = storage.Client.from_service_account_json(
        app.config['CRED_JSON'])
    bucket = storage_client.get_bucket(app.config['BUCKET_NAME'])
    listings = Listing.query.order_by(Listing.created_at.desc()).all()
    images = {}
    for listing in listings:
        listing_images = ListingImage.query.filter_by(
            listing_id=listing.id).all()
        images[listing.id] = [image.path for image in listing_images]
    image_urls = {}
    for path in set(sum(images.values(), [])):
        blob = bucket.blob(path)
        url = blob.public_url
        image_urls[path] = url
    print(image_urls)
    return render_template('index.html.j2', title=_('Carousell Hong Kong | Buy & Sell Cars, Property, Goods & Services'), listings=listings, images=images, image_urls=image_urls)
#rewrite by leo


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


#Leo code here
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

@app.route('/Payments')
def Payments():
    return render_template('Payments.html.j2', title=_('Payments'))

@app.route('/UserLocation')
def UserLocation():
    return render_template('UserLocation.html.j2', title=_('UserLocation'))

@app.route('/Discounts')
def Discounts():
    return render_template('Discounts.html.j2', title=_('Discounts'))


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    form = SellForm()
    if form.validate_on_submit():
        # Get the current user
        user = current_user
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
                          status='available',  # set the status to 'available',
                          category=category,
                          location=form.location.data,
                          user_id=user.id)  # Set the user_id attribute to the current user's id
        # Add the objects to the database
        db.session.add(category)
        db.session.add(listing)
        db.session.commit()
        # Refresh the listing object to make sure that it is fully committed to the database
        db.session.refresh(listing)
        # Set the listing_id attribute of the ListingImage object
        image.listing_id = listing.id
        print(f"listing_id: {image.listing_id}")
        db.session.add(image)
        db.session.commit()
        flash(_('Your item has been saved.'))
        return redirect(url_for('index'))
    return render_template('sell.html.j2', title=_('Sell or Give Away Items, Offer Services, or Rent Out Your Apartment on Carousell'), form=form)


@app.route('/administrator')
@admin_required
def administrator():
    form = AdminForm()
    return render_template('administrator.html.j2', title=_('administrator'), form=form)

@app.route('/product_details/<int:id>')
def product_details(id):
    # Query the database for the listing with the specified ID
    listing = Listing.query.get(id)
    category = listing.category
    user = listing.user
    storage_client = storage.Client.from_service_account_json(
        app.config['CRED_JSON'])
    bucket = storage_client.get_bucket(app.config['BUCKET_NAME'])
    # Query the database for the image paths for the current listing
    listing_images = ListingImage.query.filter_by(listing_id=id).all()
    # Create a dictionary to hold the URLs for each image path
    image_urls = {}
    # Loop through the image paths and get the URLs for each one
    for image in listing_images:
        # Get the blob for the current path
        blob = bucket.blob(image.path)
        # Get the URL for the blob
        url = blob.public_url
        # Add the URL to the image_urls dictionary
        image_urls[image.path] = url
    return render_template('product_details.html.j2', 
                           title=listing.title, 
                           listing=listing, 
                           category=category,
                           user=user,
                           listing_images=listing_images,
                           image_urls=image_urls)
#done by leo
# Alex coding here
@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and user != current_user:  # Added check for current user
            message = request.form['message']
            report = Report(user_id=user.id, message=message)
            db.session.add(report)
            db.session.commit()
            flash('Report successfully submitted!', 'success')
        elif user == current_user:  # Display an error message when a user tries to report themselves
            flash('You cannot report yourself!', 'danger')
        else:
            flash('User does not exist!', 'danger')
        return redirect(url_for('report'))
    return render_template('report.html.j2')


@app.route('/notifications')
def notifications():
    notifications = Notification.query.all()
    return render_template('notifications.html.j2', notifications=notifications)


@app.route('/notifications/create', methods=['GET', 'POST'])
def create_notification():
    if request.method == 'POST':
        content = request.form.get('content')
        user_id = 1  # replace with the actual user id
        notification = Notification(content=content, user_id=user_id)
        db.session.add(notification)
        db.session.commit()

        return redirect(url_for('notifications'))
    return render_template('create_notification.html.j2')

@app.route('/review', methods=['GET', 'POST'])
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        seller_id = form.seller.data
        content = form.content.data
        rating = form.rating.data
        if seller_id == str(current_user.id):
            flash('You cannot rate yourself!', 'danger')
        else:
            review = Review(seller_id=seller_id, buyer_id=current_user.id, content=content, rating=rating)
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted!', 'success')
            return redirect(url_for('review'))
    return render_template('review.html.j2', form=form)

@app.route('/product_details/<int:id>', methods=['GET', 'POST'])
def product_details(id):
    listing = Listing.query.get(id)
    return render_template('product_details.html.j2', listing=listing, id=id)
# jonas------

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        owner = request.form['owner']
        card_number = request.form['card_number']
        cvv = request.form['cvv']
        payment = Payment(owner=owner, card_number=card_number, cvv=cvv)
        db.session.add(payment)
        db.session.commit()
        return 'Payment successful!'
    return render_template('payment.html')

@app.route('/User_Location', methods=['GET', 'POST'])
def User_Location():
    if request.method == 'POST':
        district = request.form['district']
        address = request.form['address']
        postal_code = request.form['postal_code']
        User_Location = UserLocations(
            district=district, address=address, postal_code=postal_code)
        db.session.add(User_Location)
        db.session.commit()
        return 'ok!'
    return render_template('UserLocation.html')


@app.route('/User_Discount', methods=['GET', 'POST'])
def User_Discount():
    if request.method == 'POST':
        exchange_code = request.form['exchange_code']
        User_Discount = UserDiscounts(exchange_code=exchange_code)
        db.session.add(User_Discount)
        db.session.commit()
        return 'exchange successful!'
    return render_template('discounts.html')

