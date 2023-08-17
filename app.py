import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import secrets
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from last import process_text_data
from patos import random_text_gen


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///anmonbr.db")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'officbranmon@gmail.com'
app.config['MAIL_PASSWORD'] = 'johfjudzmuruumsx'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
users_db = {}

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def adm_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") != 5:
            return redirect("/error")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/error")
def error():
    return render_template("error.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/send_email", methods=["GET", "POST"])
@adm_required
def send_email():
    if request.method == "POST":
        email_content = request.form.get('email_content') 
        recipients = db.execute("SELECT email FROM users")
        for recipient in recipients:
            email = recipient['email']
            msg = Message('Subject', sender='officbranmon@gmail.com', recipients=[email])
            msg.body = email_content
            mail.send(msg)
        return "Email sent to all recipients!"
    else:
        return render_template("compose.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return render_template("error.html")
        session["user_id"] = rows[0]["id"]
        username = request.form.get("username")
        session["username"] = username
        id = db.execute(
            "SELECT id FROM users WHERE username = ?", username
            )
        session["id"] = id
        return redirect("/")
    else:
        return render_template("login.html")
    

@app.route("/peixe")
def peixe():
    return render_template("peixe.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        confirmation = request.form.get("confirmation")
        email = request.form['email']
        if username == "" or username == " ":
            return render_template("error.html")
        if confirmation == "" or password == "":
            return render_template("error.html")
        if password == confirmation:
            existing_user = db.execute(
                "SELECT * FROM users WHERE username = ?", username
            )
            if existing_user:
                return render_template("error.html")
            hash = generate_password_hash(password)
            token = secrets.token_hex(16)
            users_db[email] = {'token': token, 'status': 'inactive'}
            users_db[username] = username
            users_db[password] = hash
            confirmation_link = url_for('confirm_account', token=token, username=username, hash=hash, _external=True)
            msg = Message('Confirm Your Account', sender='officbranmon@gmail.com', recipients=[email])
            msg.body = f"Click the following link to confirm your account: {confirmation_link}"
            mail.send(msg)
            return redirect("/")
            
        else:
            return render_template("error.html")

    else:
        users = db.execute("SELECT * FROM users")
        return render_template("register.html", users=users)
    
def get_user_email_by_token(token):
    # Iterate through the users_db dictionary to find the email associated with the token
    for email, user_data in users_db.items():
        if user_data['token'] == token:
            return email
    return None


@app.route('/confirm')
def confirm_account():
    username = request.args.get('username')
    hash = request.args.get('hash')
    token = request.args.get('token')
    if token:
        email = get_user_email_by_token(token)
        if email and token == users_db[email]['token']:
            users_db[email]['status'] = 'active'
            db.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)", username, hash, email
            )
            return redirect("/")
    return render_template("error.html")


@app.route("/recover", methods=["GET", "POST"])
def recover():
    """Register user"""
    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        email = request.form['email']
        if confirmation == "" or password == "":
            return render_template("error.html")
        if password == confirmation:
            existing_user = db.execute(
                "SELECT * FROM users WHERE email = ?", email
            )
            if not existing_user:
                return render_template("error.html")
            hash = generate_password_hash(password)
            token = secrets.token_hex(16)
            users_db[email] = {'token': token, 'status': 'inactive'}
            users_db[password] = hash
            confirmation_link = url_for('change', token=token, hash=hash, _external=True, eemail=email)
            msg = Message('Change your password', sender='officbranmon@gmail.com', recipients=[email])
            msg.body = f"Click the following link to change your password: {confirmation_link}"
            mail.send(msg)
            return redirect("/")
            
        else:
            return render_template("error.html")

    else:
        users = db.execute("SELECT * FROM users")
        return render_template("account.html", users=users)
    
@app.route('/change')
def change():
    
    emailu = request.args.get('eemail')
    hash = request.args.get('hash')
    token = request.args.get('token')
    if token:
        email = get_user_email_by_token(token)
        if email and token == users_db[email]['token']:
            users_db[email]['status'] = 'active'
            db.execute(
                "UPDATE users SET password = ? WHERE email = ?", hash, emailu
            )
            return redirect("/")
    return render_template("error.html")

@app.route('/train')
def train():
    process_text_data()

@app.route('/text', methods=['GET', 'POST'])
def text():
    text = random_text_gen()

    if request.method == "POST":
        return render_template("text.html", text=text)
    else:
        return render_template("text.html", text=text)