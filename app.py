from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import os
import io
from PIL import Image
import hashlib
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forgery_results.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class ForgeryResult(db.Model):
    " " " Initial migration " " "
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    forgery_result = db.Column(db.String(255), nullable=False)

# Create a model for feedback
class Feedback(db.Model):
    " " " Initial migration " " "
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)

class User(db.Model):
    " " " Initial migration " " "
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

users = {
    'admin': 'adminpassword',
    'user1': 'user1password',
    'user2': 'user2password'
}

def calculate_md5(image_data):
    try:
        md5_hash = hashlib.md5(image_data).hexdigest()
        return md5_hash
    except Exception as e:
        print(f"Error calculating MD5 hash: {e}")
        return None

def detect_forgery(original_image_data, processed_image_data):
    original_md5 = calculate_md5(original_image_data)
    processed_md5 = calculate_md5(processed_image_data)

    print("Original MD5:", original_md5)
    print("Processed MD5:", processed_md5)

    if original_md5 and processed_md5:
        if original_md5 == processed_md5:
            return "Image Integrity Preserved"
        else:
            return "Image Integrity has been Compromised"
    else:
        return "Error calculating MD5 hash"

def process_image(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('L')
        return img
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route('/forgery_detection', methods=['GET', 'POST'])
def forgery_detection():
    if 'username' in session:
        forgery_result = None
        processed_image_url = None

        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                uploaded_file_data = uploaded_file.read()
                processed_image = process_image(uploaded_file_data)

                if processed_image:
                    forgery_result = detect_forgery(uploaded_file_data, processed_image.tobytes())

                    result_entry = ForgeryResult(original_filename=uploaded_file.filename, forgery_result=forgery_result)
                    db.session.add(result_entry)
                    db.session.commit()

                    flash('Image uploaded and processed successfully!', 'success')

        return render_template('forgery_detection.html', forgery_result=forgery_result, processed_image_url=processed_image_url)
    
    return redirect(url_for('login'))

@app.route('/forgery_results')
def forgery_results():
    if 'username' in session:
        results = ForgeryResult.query.all()
        return render_template('forgery_results.html', results=results)
    
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('home.html', username=username)
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/store_user_info', methods=['POST'])
def store_user_info():
    if 'username' in session:
        username = session['username']
        password = request.form['password']

        # Check if the user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = password
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)

        db.session.commit()
        flash('User information updated successfully!', 'success')

        return redirect(url_for('user_dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/store_feedback', methods=['POST'])
def store_feedback():
    if 'username' in session:
        username = session['username']
        feedback_text = request.form['feedback']

        user = User.query.filter_by(username=username).first()
        if user:
            feedback_entry = Feedback(user_id=user.id, text=feedback_text)
            db.session.add(feedback_entry)
            db.session.commit()

            flash('Feedback submitted successfully!', 'success')

        return redirect(url_for('feedback'))
    else:
        return redirect(url_for('login'))



def save_user_data(username, password):
    user_data = {}
    
    if os.path.exists('user.json') and os.path.getsize('user.json') > 0:
        with open('user.json', 'r') as user_file:
            user_data = json.load(user_file)
    user_data[username] = password

    with open('user.json', 'w') as user_file:
        json.dump(user_data, user_file)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if username not in users and password == confirm_password:
            users[username] = password
            save_user_data(username, password)

            session['username'] = username
            return redirect(url_for('login'))
        else:
            flash('Username already exists or passwords do not match', 'error')
    return render_template('signup.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('user_dashboard.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' in session:
        processed_image_url = None
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                uploaded_file_data = uploaded_file.read()
                processed_image = process_image(uploaded_file_data)

                if processed_image:
                    processed_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + uploaded_file.filename)
                    processed_image.save(processed_filename)
                    processed_image_url = url_for('static', filename='uploads/' + 'processed_' + uploaded_file.filename)

                    flash('Image uploaded and processed successfully!', 'success')
                else:
                    flash('Error processing image', 'error')
            else:
                flash('No file uploaded', 'error')

        return render_template('upload.html', processed_image_url=processed_image_url)
    
    return redirect(url_for('login'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' in session:
        if request.method == 'POST':
            feedback_text = request.form['feedback']
            # Store the feedback in your database or send it to your support team
            
            flash('Feedback submitted successfully!', 'success')

        return render_template('feedback.html')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)





