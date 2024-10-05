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


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Here you can handle the sign-up logic
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return "Passwords do not match", 400

        # Register user logic (you can later integrate a database)
        print(f"Sign Up: {email}")
        return redirect(url_for('index'))
    
    return render_template('signup.html')
if __name__ == '__main__':
    app.run(debug=True)
