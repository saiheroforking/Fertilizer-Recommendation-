from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import logging
import absl.logging

# Suppress absl warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress INFO and WARNING (but not errors)

# Disable absl logging warnings (like 'Compiled the loaded model...')

from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from functools import wraps
from models import db, bcrypt, User  # Correct imports
import config

absl.logging.set_verbosity(absl.logging.ERROR)

app = Flask(__name__)
app.secret_key = "your-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.secret_key = config.SECRET_KEY

db.init_app(app)
bcrypt.init_app(app)

# Upload folder config
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function for image preprocessing
def preprocess_image(file_path):
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

# Helper function for model prediction
def predict_image(model, img_array, class_indices):
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    class_label = list(class_indices.keys())[list(class_indices.values()).index(predicted_class)]
    return class_label

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Load models
model_1 = load_model(r"C:\Users\notla\Downloads\project_f\project\models\fertilizer_recommendation_model_v3.h5")
model_2 = load_model(r"C:\Users\notla\Downloads\project_f\project\models\fertilizer_recommendation_model.h5")

# Sample label map (replace with actual class names from your model)
fertilizer_mapping = {
    "Healthy": "No fertilizer needed",
    "Aphid": "NPK fertilizer (10:26:26) + Neem oil spray",
    "Becterial Blight": "Potassium Nitrate (13-0-45) + Zinc Sulphate",
    "Ear rot": "Balanced NPK fertilizer + Calcium Nitrate",
    "Bollworm": "DAP (18:46:0) + Neem cake",
    "Mealy bug": "Neem-based fertilizer + Potash spray",
    "Pink bollworm": "Urea + Potassium Nitrate (13-0-45)",
    "Thrips": "Potash + Micronutrient fertilizer",
    "Whitefly": "NPK (19:19:19) + Neem oil foliar spray",
    "Brown_Spot": "Use Potassium-rich fertilizer",
    "Blast": "Apply Nitrogen-based fertilizer",
    "Rust": "Use Fungicide and balanced NPK fertilizer",
    "Smut": "Apply Phosphorus-rich fertilizer",
    "Sigatoka": "Use Sulfur-based fertilizer",
    "Panama_Disease": "Apply organic compost with Phosphorus",
    "Anthracnose": "Use Copper-based fungicide",
    "Powdery_Mildew": "Apply Sulfur dust or Potassium bicarbonate",
    "Septoria leaf spot":"balanced NPK fertilizer (e.g., 10-10-10)"
}

@app.route('/')
def base():
    return render_template('base.html')

# Routes
@app.route('/home')
@login_required
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('home.html', user_name=user.first_name)
    return redirect(url_for('login'))

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/models')
@login_required
def models():
    return render_template('models.html')

@app.route('/fertilizer_info')
@login_required
def fertilizer_info():
    return render_template('fertilizer_info.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered.")
            return redirect(url_for('signup'))

        # Password match check
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))

        # Hash the password securely
        hashed_password = generate_password_hash(password)

        # Create and save new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.first_name  # Add this
            flash(f"Welcome back, {user.first_name}!")
            return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/model1', methods=['GET', 'POST'])
def model1():
    result = None
    class_label = None
    uploaded_img = None

    if request.method == 'POST':
        file = request.files.get('image_file')
        if not file or file.filename == '':
            flash('No image file selected.')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        uploaded_img = filename  # Just the filename for display in HTML

        # Preprocess
        img_array = preprocess_image(filepath)

        # Load classes from dataset
        dataset_dir = r"C:\Users\notla\OneDrive\Desktop\dataset"
        datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            rotation_range=30,
            zoom_range=0.2,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        train_generator = datagen.flow_from_directory(
            directory=dataset_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )

        class_indices = train_generator.class_indices
        class_label = predict_image(model_1, img_array, class_indices)
        recommendation = fertilizer_mapping.get(class_label, "No recommendation available")

    return render_template('model1.html', result=class_label, uploaded_img=uploaded_img)

@app.route('/model2', methods=['GET', 'POST'])
def model2():
    result = None
    uploaded_img = None
    recommendation = None

    if request.method == 'POST':
        file = request.files.get('image_file')
        if not file or file.filename == '':
            flash('No image file selected.')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        uploaded_img = filename  # Just the filename for display in HTML

        # Preprocess
        img_array = preprocess_image(filepath)
        dataset_dir = r"C:\Users\notla\OneDrive\Desktop\dataset"
        datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            rotation_range=30,
            zoom_range=0.2,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        train_generator = datagen.flow_from_directory(
            directory=dataset_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )

        class_indices = train_generator.class_indices
        class_label = predict_image(model_1, img_array, class_indices)
        recommendation = fertilizer_mapping.get(class_label, "No recommendation available")

    return render_template('model2.html', result=recommendation, uploaded_img=uploaded_img)

@app.route('/model3', methods=['GET', 'POST'])
def model3():
    result = "Mock Prediction Result from Model 3 - MobileNet"
    return render_template('model3.html', result=result)

@app.route('/model4', methods=['GET', 'POST'])
def model4():
    result = None
    recommendation = None
    uploaded_img = None

    if request.method == 'POST':
        file = request.files.get('image_file')
        if not file or file.filename == '':
            flash('No image file selected.')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        uploaded_img = filename  # Just the filename for display in HTML

        # Preprocess
        img_array = preprocess_image(filepath)

        # Load classes from dataset
        dataset_dir = r"C:\Users\notla\OneDrive\Desktop\dataset"
        datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            rotation_range=30,
            zoom_range=0.2,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        train_generator = datagen.flow_from_directory(
            directory=dataset_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )

        class_indices = train_generator.class_indices
        class_label = predict_image(model_1, img_array, class_indices)
        recommendation = fertilizer_mapping.get(class_label, "No recommendation available")

    return render_template('model4.html', result=recommendation, uploaded_img=uploaded_img)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)  # Clear this too
    flash("Logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
