from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_mail import Message
import random
import os

auth = Blueprint('auth', __name__)

# In-memory user db, OTP store, and verification store (demo only)
users = {}
otp_store = {}
verification_store = {}  # Store unverified users

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def send_email(mail, subject, recipient, html_content):
    try:
        msg = Message(
            subject=subject,
            sender="somuuppara43@gmail.com",
            recipients=[recipient],
            html=html_content
        )
        mail.send(msg)
        print(f"✅ Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {e}")
        return False

@auth.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        # Check if user exists and is verified
        if email in verification_store:
            flash('Please verify your email first. Check your inbox for verification code.')
            session['verification_email'] = email
            return redirect(url_for('auth.verify_email'))
        
        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            flash('Welcome back!')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        from flask import current_app
        mail = current_app.extensions['mail']
        
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        
        if not is_valid_email(email):
            flash('Invalid email address')
            return redirect(url_for('auth.register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('auth.register'))
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.register'))
        if email in users or email in verification_store:
            flash('Email already registered')
            return redirect(url_for('auth.register'))
        
        # Generate verification OTP
        verification_otp = random.randint(100000, 999999)
        
        # Store user data temporarily in verification_store
        verification_store[email] = {
            'password': generate_password_hash(password),
            'name': name or 'User',
            'otp': str(verification_otp)
        }
        
        # Send verification email with attractive design
        html_content = f"""
        <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 40px; font-family: Arial, sans-serif;">
            <div style="background: #f9efdb; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color: #6d4c41; margin-bottom: 20px;">🎉 Welcome to Personal Storage!</h2>
                <p style="color: #3e2723; font-size: 16px; margin-bottom: 20px;">Thank you for registering! Please verify your email address to complete your account setup.</p>
                <p style="color: #3e2723; font-size: 16px; margin-bottom: 30px;">Your verification code is:</p>
                <div style="background: #ffb300; color: #3e2723; font-size: 24px; font-weight: bold; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    {verification_otp}
                </div>
                <p style="color: #3e2723; font-size: 14px;">This code will expire in 15 minutes.</p>
                <p style="color: #6d4c41; font-size: 12px; margin-top: 30px;">If you didn't create this account, please ignore this email.</p>
            </div>
        </div>
        """
        
        email_sent = send_email(mail, '🔐 Verify Your Email - Personal Storage', email, html_content)
        if email_sent:
            session['verification_email'] = email
            flash('Registration successful! Please check your email for verification code.')
            return redirect(url_for('auth.verify_email'))
        else:
            verification_store.pop(email, None)
            flash('Registration failed. Please try again.')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = session.get('verification_email')
    if not email or email not in verification_store:
        flash('Verification session expired. Please register again.')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        from flask import current_app
        mail = current_app.extensions['mail']
        
        entered_otp = request.form.get('otp', '').strip()
        stored_data = verification_store.get(email)
        
        if not stored_data or stored_data['otp'] != entered_otp:
            flash('Invalid verification code. Please try again.')
            return redirect(url_for('auth.verify_email'))
        
        # Move user from verification_store to users (activate account)
        users[email] = {
            'password': stored_data['password'],
            'name': stored_data['name']
        }
        
        # Create user folder
        os.makedirs(os.path.join('uploads', email), exist_ok=True)
        
        # Clean up verification data
        verification_store.pop(email, None)
        session.pop('verification_email', None)
        
        # Send welcome email
        welcome_html = f"""
        <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 40px; font-family: Arial, sans-serif;">
            <div style="background: #f9efdb; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color: #6d4c41; margin-bottom: 20px;">🎊 Account Verified Successfully!</h2>
                <p style="color: #3e2723; font-size: 16px; margin-bottom: 20px;">Welcome to Personal Storage, <strong>{stored_data['name']}</strong>!</p>
                <div style="background: #ffb300; color: #3e2723; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold;">Your account is now active!</p>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">You can now securely store and manage your photos and videos.</p>
                </div>
                <p style="color: #3e2723; font-size: 14px;">You can now log in and start uploading your files.</p>
                <p style="color: #6d4c41; font-size: 12px; margin-top: 30px;">Thank you for choosing our service!</p>
            </div>
        </div>
        """
        
        send_email(mail, '🎉 Welcome to Personal Storage!', email, welcome_html)
        flash('Email verified successfully! You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('verify_email.html', email=email)

@auth.route('/resend-verification', methods=['POST'])
def resend_verification():
    from flask import current_app
    mail = current_app.extensions['mail']
    
    email = session.get('verification_email')
    if not email or email not in verification_store:
        flash('No verification session found. Please register again.')
        return redirect(url_for('auth.register'))
    
    # Generate new OTP
    new_otp = random.randint(100000, 999999)
    verification_store[email]['otp'] = str(new_otp)
    
    # Send new verification email
    html_content = f"""
    <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 40px; font-family: Arial, sans-serif;">
        <div style="background: #f9efdb; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h2 style="color: #6d4c41; margin-bottom: 20px;">🔄 New Verification Code</h2>
            <p style="color: #3e2723; font-size: 16px; margin-bottom: 30px;">Here's your new verification code:</p>
            <div style="background: #ffb300; color: #3e2723; font-size: 24px; font-weight: bold; padding: 15px; border-radius: 8px; margin: 20px 0;">
                {new_otp}
            </div>
            <p style="color: #3e2723; font-size: 14px;">This code will expire in 15 minutes.</p>
        </div>
    </div>
    """
    
    send_email(mail, '🔐 New Verification Code - Personal Storage', email, html_content)
    flash('New verification code sent to your email!')
    return redirect(url_for('auth.verify_email'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        from flask import current_app
        mail = current_app.extensions['mail']
        
        email = request.form.get('email', '').lower().strip()
        if email not in users:
            flash('Email not registered or not verified')
            return redirect(url_for('auth.forgot_password'))
        
        otp = random.randint(100000, 999999)
        otp_store[email] = str(otp)
        
        # Send OTP email
        html_content = f"""
        <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 40px; font-family: Arial, sans-serif;">
            <div style="background: #f9efdb; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color: #6d4c41; margin-bottom: 20px;">🔐 Password Reset Request</h2>
                <p style="color: #3e2723; font-size: 16px; margin-bottom: 30px;">Your OTP for password reset is:</p>
                <div style="background: #ffb300; color: #3e2723; font-size: 24px; font-weight: bold; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    {otp}
                </div>
                <p style="color: #3e2723; font-size: 14px;">This OTP will expire in 10 minutes.</p>
                <p style="color: #6d4c41; font-size: 12px; margin-top: 30px;">If you didn't request this, please ignore this email.</p>
            </div>
        </div>
        """
        
        send_email(mail, 'Password Reset OTP', email, html_content)
        session['reset_email'] = email
        flash('OTP sent to your email. Please check your inbox.')
        return redirect(url_for('auth.reset_password'))
    return render_template('forgot_password.html')

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash('Session expired. Please start the password reset process again.')
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        from flask import current_app
        mail = current_app.extensions['mail']
        
        otp_input = request.form.get('otp', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if otp_store.get(email) != otp_input:
            flash('Invalid or expired OTP')
            return redirect(url_for('auth.reset_password'))
        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('auth.reset_password'))
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.reset_password'))
        
        users[email]['password'] = generate_password_hash(password)
        otp_store.pop(email, None)
        session.pop('reset_email', None)
        
        # Send confirmation email
        html_content = f"""
        <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 40px; font-family: Arial, sans-serif;">
            <div style="background: #f9efdb; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color: #6d4c41; margin-bottom: 20px;">✅ Password Reset Successful</h2>
                <p style="color: #3e2723; font-size: 16px; margin-bottom: 20px;">Your password has been updated successfully!</p>
                <div style="background: #ffb300; color: #3e2723; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <strong>Account: {email}</strong>
                </div>
                <p style="color: #3e2723; font-size: 14px; margin-bottom: 20px;">You can now log in with your new password.</p>
                <p style="color: #d32f2f; font-size: 12px;">If you did not perform this action, please contact support immediately.</p>
                <hr style="border: none; height: 1px; background: #b3926f; margin: 20px 0;">
                <p style="color: #6d4c41; font-size: 12px;">Thank you for using our service!</p>
            </div>
        </div>
        """
        
        send_email(mail, 'Password Reset Confirmation', email, html_content)
        flash('Password reset successful! You can now log in.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')

@auth.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out')
    return redirect(url_for('auth.login'))
