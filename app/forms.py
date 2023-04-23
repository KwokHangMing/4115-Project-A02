from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, FileField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from flask_wtf.file import FileRequired
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class SellForm(FlaskForm):
    category = SelectField(_l('Category'), choices=[('Electronics'), ('Fashion'), ('Luxury'), ('Services'), ('Cars'), ('Property')])
    title = TextAreaField(_l('Listing Title'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[DataRequired()])
    price = IntegerField(_l('Price'), validators=[DataRequired()])
    location = SelectField(_l('Location'), choices=[('All of Hong Kong'), ('Hong Kong Island'), ('Kowloon'), ('New Territories')])
    image = FileField(_l('Select Photos', validators=[FileRequired()]))
    status = HiddenField(default='available') 
    submit = SubmitField(_l('List now'))

class AdminForm(FlaskForm):
    title = TextAreaField(_l('Title'), validators=[DataRequired()])
    image_url = TextAreaField(_l('Image URL'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

# Alex coding here
class ReportForm(FlaskForm):
    message = StringField('report content', validators=[DataRequired()])
    submit = SubmitField('submit report')

class ReviewForm(FlaskForm):
    seller = SelectField('Seller', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired()])
    submit = SubmitField('Submit')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seller.choices = [(str(u.id), u.username) for u in User.query.all() if u != current_user]
