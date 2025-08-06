
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import pymysql

# Use pymysql instead of MySQLdb
pymysql.install_as_MySQLdb()

# Load config
with open('parmas.json', 'r') as c:
    params = json.load(c)["parmas"]

# Flask app initialization
app = Flask(__name__, static_folder='statics')

# Email configuration
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['user_name'],
    MAIL_PASSWORD=params['password']
)
mail = Mail(app)

# Database configuration
local_server = False  # Set False for production
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_url']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------
# Database Models
# -----------------------
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

# -----------------------
# Routes
# -----------------------

@app.route("/")
def home():
    return render_template("index.html", parmas=params)

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        try:
            # Send admin email
            mail.send_message(
                subject=f'New message from {name}',
                sender=params['user_name'],
                recipients=[params['user_name']],
                body=f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\n{message}"
            )

            # Send user confirmation email
            mail.send_message(
                subject='Thank you for contacting us',
                sender=params['user_name'],
                recipients=[email],
                body=f"Dear {name},\n\nThanks for contacting us.\n\nSubject: {subject}\nMessage: {message}\n\nWe’ll get back to you soon.\n\n– Team"
            )

            print("✅ Email sent and data saved.")
            print(f"Sending email to: {email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")


        except Exception as e:
            print(f"❌ Error: {e}")

    return render_template("index.html", parmas=params)
if __name__ == "__main__":
    with app.app_context():        # ✅ Important: Needed for SQLAlchemy context
        db.create_all()            # ✅ Creates tables automatically if not exist
    app.run(debug=True, port=8060)


