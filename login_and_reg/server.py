from flask import Flask, redirect, render_template, request, session,flash
from mysqlconnection import MySQLConnector
from os import urandom
from binascii import b2a_hex
from md5 import new as md5_new
import re

app = Flask(__name__)
mysql = MySQLConnector(app,"login")
app.secret_key = "LaLlaveSecreta"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    if "logged_in" not in session:
        session["logged_in"] = False
    if "current_user" not in session:
        session["current_user"] = ""

    if session["logged_in"]:
        return render_template('user.html')
    else:
        return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        email = request.form["email"]
        password = request.form["password"]
        query = "select email, password, salt from users where email = :email"
        user = mysql.query_db(query,{ "email": email } )
        if len(user) == 0:
            flash("Email was not found!")
        elif md5_new(password + user[0]["salt"]).hexdigest() == user[0]["password"]:
            session["current_user"] = email
            session["logged_in"] = True
            return render_template('user.html')
        else:
            flash("Password incorrect")
        return redirect('/login')

@app.route('/signup',methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    pass_conf = request.form["pass_conf"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    if len(password) < 8:
        flash("You password must be greater than 8 characters!")
    elif password != password:
        flash("Your passwords do not match!")
    elif not EMAIL_REGEX.match(email):
        flash("Not a valid email!")
    elif len(first_name) < 2:
        flash("First name must be greater than 2 characters")
    elif len(last_name) < 2:
        flash("Last name must be greater than 2 characters")
    else:
        query = "INSERT into USERS (email, password, first_name, last_name, created_at, salt) VALUES (:email, :password, :first_name, :last_name, NOW(), :salt)"
        salt = b2a_hex(urandom(15))
        data = {
            "email": email,
            "password": md5_new(password + salt).hexdigest(),
            "salt": salt,
            "first_name": first_name,
            "last_name": last_name
        }
        mysql.query_db(query,data)
        session["logged_in"] = True
        session["current_user"] = email
    return redirect('/')

@app.route("/logout")
def logout():
    session["logged_in"] = False
    session["current_user"] = ""
    return redirect('/')






app.run(debug=True)
