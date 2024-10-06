from flask import Flask, render_template, request, redirect, url_for, Response, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Initialize counters
counter = 0
stage = None

# Function to calculate the angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)  # First point (shoulder)
    b = np.array(b)  # Second point (elbow)
    c = np.array(c)  # Third point (wrist)

    # Calculate the angle using arctangent
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    # Ensure the angle is within [0, 180] range
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Video capture setup
camera = cv2.VideoCapture(1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    global counter, stage
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Recolor the image to RGB as required by MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make pose detection
            results = pose.process(image)

            # Recolor back to BGR for rendering
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for right arm (you can switch to left arm)
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                # Calculate the angle at the elbow joint
                angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

                # Visualize the angle on the screen
                cv2.putText(image, f'Elbow Angle: {int(angle)}',
                            tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Curl counter logic: Detect when the arm is fully extended or contracted
                if angle > 160:
                    stage = "down"
                if angle < 30 and stage == "down":
                    stage = "up"
                    counter += 1  # Count each curl when the user moves from "down" to "up"
                    print(f"Reps: {counter}")

                # Display feedback based on form
                if angle > 160:
                    feedback = "Fully Extended"
                elif angle < 30:
                    feedback = "Fully Contracted"
                else:
                    feedback = "Keep Curling"

                # Show feedback on the frame
                cv2.putText(image, feedback,
                            (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                # Display the rep count on the frame
                cv2.putText(image, f'Reps: {counter}',
                            (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            except:
                pass

            # Render the pose annotations on the frame
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()

            # Yield the frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Define Profile model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    surgery_type = db.Column(db.String(100), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()
# Landing Page route
@app.route('/')
def index():
    return render_template('index.html')

# Sign-Up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Save the user in the database
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('create_profile'))
        else:
            error = "Passwords do not match."
            return render_template('signup.html', error=error)

    return render_template('signup.html')

# Sign-In route
# Sign-In route
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None  # Initialize error message variable
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find the user in the database
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            # If the user does not exist
            error = "No account found."
        elif not check_password_hash(user.password, password):
            # If the password does not match
            error = "Wrong email or password."
        else:
            # Successful sign-in
            session['user'] = user.email  # Save user info in the session
            return redirect(url_for('home'))
    
    return render_template('signin.html', error=error)


# Create Profile route
@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        surgery_type = request.form['surgery_type']

        # Find the user based on the email in the session
        user = User.query.filter_by(email=session['user']).first()
        if user:
            new_profile = Profile(user_id=user.id, name=name, age=age, gender=gender, surgery_type=surgery_type)
            db.session.add(new_profile)
            db.session.commit()

        return redirect(url_for('home'))

    return render_template('create_profile.html')
@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/excercise')
def excercise():
    return render_template('excercise.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Home route
@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
