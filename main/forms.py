from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from main.models import User

class SignUpForm(FlaskForm):
    """Sign up form"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters')
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Invalid email address')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters long')
        ]
    )
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username) -> None:
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email) -> None:
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one or log in.')

class LoginForm(FlaskForm):
    """Login form - accept username or email"""
    identifier = StringField(
        'Username or Email',
        validators=[
            DataRequired(message='Please enter your username or email')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class UpdateProfileForm(FlaskForm):
    """Update user profile form"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ]
    )
    first_name = StringField('First Name', validators=[Length(max=120)])
    last_name = StringField('Last Name', validators=[Length(max=120)])
    bio = StringField('Bio', validators=[Length(max=500)])
    country = StringField('Country', validators=[Length(max=120)])
    submit = SubmitField('Update Profile')
    
    def validate_username(self, username) -> None:
        """Check if username is available (excluding current user)"""
        if username.data is not None:
            user = User.query.filter_by(username=username.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('Username already taken.')
    
    def validate_email(self, email) -> None:
        """Check if email is available (excluding current user)"""
        if email.data is not None:
            user = User.query.filter_by(email=email.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('Email already registered.')
    
    def set_user_id(self, user_id: int) -> None:
        """Set current user ID for validation"""
        self.user_id = user_id
