from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Sign In route
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Example Sign In logic
        email = request.form['email']
        password = request.form['password']

        # Authentication logic (simplified here)
        if email == 'user@example.com' and password == 'password':  # Replace with actual user validation
            return redirect(url_for('home'))
        else:
            return "Invalid login", 401

    return render_template('signin.html')

# Home Page route
@app.route('/home')
def home():
    return render_template('home.html')


# Sign-Up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Here you would handle the sign-up logic
        email = request.form['email']
        password = request.form['password']

        # Add logic to save the user (not implemented here)
        
        # Redirect to Create Profile page after successful sign-up
        return redirect(url_for('create_profile'))

    return render_template('signup.html')

# Create Profile route
@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        # Here you would handle the profile creation logic
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        surgery_type = request.form['surgery_type']

        # Process the profile data (save it to a database, etc.)
        # Redirect to the home page after creation
        return redirect(url_for('home'))

    return render_template('create_profile.html')

if __name__ == '__main__':
    app.run(debug=True)
