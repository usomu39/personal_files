from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv'}

# Gmail SMTP Configuration - UPDATED with your NEW app password
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'somuuppara43@gmail.com'
# Your NEW App Password: lucs iluq pzqg mzxt = lucsiluqpzqgmzxt (no spaces)
app.config['MAIL_PASSWORD'] = 'lucsiluqpzqgmzxt'
app.config['MAIL_DEFAULT_SENDER'] = 'somuuppara43@gmail.com'

mail = Mail(app)

# Import auth blueprint
from auth import auth, users

app.register_blueprint(auth)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_logged_in():
    return 'email' in session

def is_admin():
    return session.get('is_admin', False)

@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

# Email test route
@app.route('/test-email')
def test_email():
    try:
        from flask_mail import Message
        print("🧪 Testing Gmail SMTP with new password...")
        
        msg = Message(
            subject='🎉 Gmail SMTP Test - Personal Storage',
            sender='somuuppara43@gmail.com',
            recipients=['somuuppara43@gmail.com'],
            html='''
            <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5ebe0, #ffb300); padding: 40px; font-family: Arial, sans-serif;">
                <div style="background: #f9efdb; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <h2 style="color: #6d4c41;">🎊 Gmail SMTP Working!</h2>
                    <p style="color: #3e2723; font-size: 16px;">Your Personal Storage app can now send emails successfully!</p>
                    <div style="background: #ffb300; color: #3e2723; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <strong>✅ Email verification is now enabled</strong>
                    </div>
                    <p style="color: #6d4c41; font-size: 12px;">Test completed at: ''' + str(__import__('datetime').datetime.now()) + '''</p>
                </div>
            </div>
            '''
        )
        mail.send(msg)
        print("✅ Test email sent successfully!")
        return "✅ Test email sent successfully! Check your Gmail inbox at somuuppara43@gmail.com"
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return f"❌ Email test failed: {str(e)}"

# Admin routes
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            flash('Admin logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    all_users = {}
    total_files = 0
    
    for email, user_data in users.items():
        try:
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], email)
            files = os.listdir(user_folder) if os.path.exists(user_folder) else []
            file_count = len(files)
            total_files += file_count
            
            all_users[email] = {
                'name': user_data.get('name', 'User'),
                'file_count': file_count,
                'files': files
            }
        except:
            all_users[email] = {
                'name': user_data.get('name', 'User'),
                'file_count': 0,
                'files': []
            }
    
    from auth import verification_store
    stats = {
        'total_users': len(users),
        'total_files': total_files,
        'pending_verifications': len(verification_store)
    }
    
    return render_template('admin_dashboard.html', users=all_users, stats=stats)

@app.route('/admin/delete-user/<email>', methods=['POST'])
def admin_delete_user(email):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if email in users:
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], email)
        if os.path.exists(user_folder):
            import shutil
            shutil.rmtree(user_folder)
        users.pop(email, None)
        flash(f'User {email} deleted successfully!')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Admin logged out')
    return redirect(url_for('admin_login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    email = session['email']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], email)
    os.makedirs(user_folder, exist_ok=True)
    
    try:
        files = os.listdir(user_folder)
    except:
        files = []
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_folder, filename))
            flash('File uploaded successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type')
            
    return render_template('dashboard.html', files=files, email=email, name=users[email].get('name', 'User'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    email = session['email']
    user = users.get(email)
    
    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        if new_name:
            user['name'] = new_name
            flash('Profile updated successfully!')
        else:
            flash('Name cannot be empty')
        return redirect(url_for('profile'))
    
    try:
        upload_count = len(os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], email)))
    except:
        upload_count = 0
        
    return render_template('profile.html', email=email, name=user.get('name', 'User'), upload_count=upload_count)

@app.route('/uploads/<email>/<filename>')
def uploaded_file(email, filename):
    if not is_logged_in() or session['email'] != email:
        flash('Unauthorized access')
        return redirect(url_for('auth.login'))
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], email), filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    email = session['email']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], email, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully!')
    else:
        flash('File not found')
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("🚀 Starting Personal Storage App...")
    print("📧 Gmail: somuuppara43@gmail.com")
    print("🔑 New App Password configured")
    print("🌐 Main App: http://localhost:5000")
    print("🧪 Test Email: http://localhost:5000/test-email")
    print("⚙️ Admin Portal: http://localhost:5000/admin-login (admin/admin123)")
    app.run(debug=True, host='0.0.0.0', port=5000)
