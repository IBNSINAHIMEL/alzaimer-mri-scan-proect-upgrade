from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from model_loader import model_predictor
import mysql.connector
from mysql.connector import Error
import os
import hashlib
import time
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'alzheimer_secret_key_2024'
CORS(app)

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# MySQL Database Configuration for XAMPP
class Database:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = ''  # XAMPP default is empty
        self.database = 'alzheimer_app'
    
    def get_connection(self, retries=3, delay=2):
        """Create connection with retry logic"""
        for attempt in range(retries):
            try:
                connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    auth_plugin='mysql_native_password',
                    connection_timeout=30
                )
                
                if connection.is_connected():
                    print(f"✅ Database connection established (attempt {attempt + 1})")
                    return connection
                    
            except Error as e:
                print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    print(f"🔄 Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("❌ All connection attempts failed")
                    return None
        
        return None
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute query with proper connection handling"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return True
                
        except Error as e:
            print(f"❌ Query execution failed: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def check_database_exists(self):
        """Check if database and tables exist"""
        try:
            # First check if we can connect to MySQL
            test_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                auth_plugin='mysql_native_password'
            )
            test_conn.close()
            
            # Now check if our database exists
            connection = self.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = 'users'
            """, (self.database,))
            users_table_exists = cursor.fetchone()[0] > 0
            cursor.close()
            connection.close()
            
            return users_table_exists
                
        except Error as e:
            print(f"❌ Error checking database: {e}")
            return False
    
    def authenticate_user_by_username_or_email(self, username_or_email, password):
        """Improved authentication with better error handling"""
        query = "SELECT * FROM users WHERE (username = %s OR email = %s) AND password = %s"
        params = (username_or_email, username_or_email, hash_password(password))
        
        result = self.execute_query(query, params)
        
        if result and len(result) > 0:
            user = result[0]
            print(f"✅ User {user['username']} authenticated successfully!")
            return user
        else:
            print(f"❌ Authentication failed for {username_or_email}")
            return None
    
    def check_user_exists(self, username, email):
        """Check if user exists"""
        query = "SELECT id FROM users WHERE username = %s OR email = %s"
        params = (username, email)
        
        result = self.execute_query(query, params)
        return result is not None and len(result) > 0
    
    def register_user(self, user_data):
        """Register user with transaction"""
        query = '''
            INSERT INTO users (username, email, birth_year, gender, blood_group, address, password, register_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        params = (
            user_data['username'],
            user_data['email'],
            user_data['birth_year'],
            user_data['gender'],
            user_data['blood_group'],
            user_data['address'],
            hash_password(user_data['password']),
            datetime.now()
        )
        
        result = self.execute_query(query, params, fetch=False)
        if result:
            print(f"✅ User {user_data['username']} registered successfully!")
            return True
        else:
            print(f"❌ Registration failed for {user_data['username']}")
            return False
    
    def save_prediction(self, user_id, image_filename, prediction_result, confidence, prediction_details):
        """Save prediction to database"""
        query = '''
            INSERT INTO predictions (user_id, image_path, prediction_result, confidence, prediction_date)
            VALUES (%s, %s, %s, %s, %s)
        '''
        
        # Store as JSON string
        result_with_details = json.dumps({
            "prediction": prediction_result,
            "confidence": confidence,
            "details": prediction_details
        })
        
        params = (
            user_id,
            image_filename,
            result_with_details,
            confidence,
            datetime.now()
        )
        
        result = self.execute_query(query, params, fetch=False)
        if result:
            print(f"✅ Prediction saved for user {user_id}")
            return True
        else:
            print(f"❌ Error saving prediction for user {user_id}")
            return False
    
    def get_user_predictions(self, user_id):
        """Get user predictions"""
        query = "SELECT * FROM predictions WHERE user_id = %s ORDER BY prediction_date DESC"
        result = self.execute_query(query, (user_id,))
        
        if result:
            for prediction in result:
                try:
                    result_data = json.loads(prediction['prediction_result'])
                    prediction['parsed_result'] = result_data
                except:
                    prediction['parsed_result'] = {
                        'prediction': prediction['prediction_result'],
                        'confidence': prediction['confidence']
                    }
        
        return result or []

# Initialize database
db = Database()

# Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        print("📝 Registration attempt received...")
        
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required!'})
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters!'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters!'})
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match!'})
        
        if db.check_user_exists(username, email):
            return jsonify({'success': False, 'message': 'Username or email already exists!'})
        
        user_data = {
            'username': username,
            'email': email,
            'birth_year': int(request.form.get('birth_year', 1990)),
            'gender': request.form.get('gender', 'Other'),
            'blood_group': request.form.get('blood_group', 'O+'),
            'address': request.form.get('address', ''),
            'password': password
        }
        
        if db.register_user(user_data):
            # Auto-login after registration
            user = db.authenticate_user_by_username_or_email(username, password)
            if user:
                session['user'] = user['username']
                session['user_id'] = user['id']
                session['user_data'] = user
            
            return jsonify({
                'success': True, 
                'message': 'Registration successful! Redirecting...'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Registration failed! Please try again.'
            })
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'})

@app.route('/login', methods=['POST'])
def login():
    try:
        print("🔐 Login attempt received...")
        
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"📧 Login attempt - Username/Email: {username_or_email}")
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'message': 'Username/Email and password are required!'})
        
        user = db.authenticate_user_by_username_or_email(username_or_email, password)
        if user:
            session['user'] = user['username']
            session['user_id'] = user['id']
            session['user_data'] = user
            print(f"✅ Login successful for user: {user['username']}")
            return jsonify({
                'success': True, 
                'message': 'Login successful! Redirecting...'
            })
        else:
            print(f"❌ Login failed for: {username_or_email}")
            return jsonify({
                'success': False, 
                'message': 'Invalid username/email or password!'
            })
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'})
@app.route('/detect')
def detect():
    """MRI Detection page - accessible even when logged in"""
    return render_template('index.html')    

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    patients = [
        {'id': 1, 'name': 'John Doe', 'last_test': '2024-01-15', 'status': 'stable', 'avatar': 'patient1.jpg'},
        {'id': 2, 'name': 'Jane Smith', 'last_test': '2024-01-14', 'status': 'improving', 'avatar': 'patient2.jpg'},
        {'id': 3, 'name': 'Robert Johnson', 'last_test': '2024-01-13', 'status': 'monitoring', 'avatar': 'patient3.jpg'},
        {'id': 4, 'name': 'Sarah Wilson', 'last_test': '2024-01-12', 'status': 'stable', 'avatar': 'patient4.jpg'},
        {'id': 5, 'name': 'Michael Brown', 'last_test': '2024-01-11', 'status': 'improving', 'avatar': 'patient5.jpg'}
    ]
    
    user_data = {
        'username': session.get('user'),
        'name': session.get('user_data', {}).get('username', 'Doctor'),
        'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    user_predictions = db.get_user_predictions(session.get('user_id'))
    
    return render_template('dashboard.html', 
                         user=user_data, 
                         patients=patients,
                         predictions=user_predictions[:5])

@app.route('/logout')
def logout():
    username = session.get('user', 'Unknown')
    session.clear()
    print(f"👋 User {username} logged out")
    return redirect(url_for('home'))

@app.route('/results')
def results_history():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user_predictions = db.get_user_predictions(session.get('user_id'))
    return render_template('results-history.html', predictions=user_predictions)

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user_data = session.get('user_data', {})
    return render_template('settings.html', user=user_data)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Please login to use prediction feature"}), 401

        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not image_file.mimetype.startswith('image/'):
            return jsonify({"error": "Invalid file type. Please upload an image."}), 400

        print(f"📸 Processing image: {image_file.filename} for user: {session.get('user')}")

        if model_predictor.model is None:
            try:
                print("🔄 Loading model...")
                model_predictor.load_model()
            except Exception as e:
                print(f"❌ Model loading failed: {e}")
                return jsonify({"error": f"Model loading failed: {str(e)}"}), 500

        print("🔮 Running prediction...")
        result = model_predictor.predict(image_file)
        print(f"✅ Prediction result: {result}")

        db.save_prediction(
            user_id=session.get('user_id'),
            image_filename=image_file.filename,
            prediction_result=result["prediction"],
            confidence=result["confidence"],
            prediction_details=result["all_predictions"]
        )

        return jsonify({
            "success": True,
            "prediction": result["prediction"],
            "confidence": round(result["confidence"], 4),
            "all_predictions": result["all_predictions"],
            "message": "Prediction completed successfully!"
        })

    except Exception as e:
        print(f"❌ Error in /predict route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/test-db')
def test_db():
    """Test database connection"""
    if db.check_database_exists():
        return jsonify({
            'success': True, 
            'message': '✅ Database connection successful!',
            'schema': 'existing_database'
        })
    else:
        return jsonify({
            'success': False, 
            'message': '❌ Database connection failed!'
        })

@app.route('/create-admin-user')
def create_admin_user():
    """Create a guaranteed working user"""
    try:
        test_user = {
            'username': 'admin',
            'email': 'admin@hospital.com',
            'birth_year': 1985,
            'gender': 'Male',
            'blood_group': 'O+',
            'address': 'Hospital Admin',
            'password': 'admin123'
        }
        
        if db.register_user(test_user):
            return jsonify({
                'success': True,
                'message': '✅ Admin user created successfully!',
                'credentials': {
                    'username': 'admin',
                    'password': 'admin123'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ Failed to create admin user'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# Check database on startup
with app.app_context():
    try:
        if db.check_database_exists():
            print("✅ Existing database detected and compatible!")
        else:
            print("❌ No compatible database found. Please ensure your database is set up.")
    except Exception as e:
        print(f"❌ Database compatibility check error: {e}")

if __name__ == '__main__':
    print("🚀 Starting Alzheimer Detection Backend...")
    print("🔗 Checking MySQL database compatibility...")
    
    if db.check_database_exists():
        print("✅ Database is COMPATIBLE with your existing schema!")
    else:
        print("❌ Database NOT FOUND or INCOMPATIBLE!")
        print("💡 Please ensure your database is set up with:")
        print("   - Database name: alzheimer_app")
        print("   - Tables: users, predictions")
    
    print("📋 Available routes:")
    print("   http://localhost:5000/ - Home page (MRI Detection)")
    print("   http://localhost:5000/register - Registration")
    print("   http://localhost:5000/login - Login") 
    print("   http://localhost:5000/dashboard - Dashboard (requires login)")
    print("   http://localhost:5000/test-db - Test database connection")
    print("   http://localhost:5000/create-admin-user - Create test user")
    print("   http://localhost:5000/predict - MRI Prediction (requires login)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)