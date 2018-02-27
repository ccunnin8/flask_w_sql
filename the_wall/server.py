from flask import Flask, redirect, render_template, flash, request,session
from mysqlconnection import MySQLConnector
from os import urandom
from binascii import b2a_hex
from md5 import new as md5_new
from validate_email import validate_email
import re

app = Flask(__name__)
app.secret_key = "EstoEsElSecreto"
mysql = MySQLConnector(app,"thewall")
#password verfiy regex
PASSWORD_REGEX = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})")
#ROUTER
@app.route('/')
def index():
    if "logged_in" not in session:
        session["logged_in"] = False

    if session["logged_in"]:
        return redirect('/wall')
    else:
        return render_template("login.html")

@app.route('/login',methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    results = email_exists(email)
    if  len(results) == 0 :
        flash("User not found!")
        return redirect('/')
    else:
        salt = results[0]["salt"]
        hashed_password = hash_password(password,salt)
        if hashed_password == results[0]["password"]:
            save_logged_in_user(results[0])
            return redirect('/wall')
        else:
            flash("The password you entered was incorrect!")
            return redirect('/')

@app.route('/post_message',methods=["POST"])
def post_message():
    pass

@app.route('/post_comment',methods=["POST"])
def post_comment():
    pass

@app.route('/logout',methods=["POST","GET"])
def logout():
    logout_user()
    return redirect('/')

@app.route('/register',methods=["POST","GET"])
def register_page():
    if request.method == "POST":
        #get all info from request.form
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]

        #form validation
        if password != password2:
            flash("Passwords do not match")
        elif len(password) < 8 or not PASSWORD_REGEX.match(password):
            flash("Your password must be at least 8 characters and include uppercase, lowercase, number, and special char")
        elif len(email_exists(email)) != 0:
            flash("Username already exists!")
            return redirect('/')
        elif len(first_name) < 2:
            flash("First name must be greater than 2 characters")
        elif len(last_name) < 2:
            flash("Last name must be greater than 2 characters")
        elif not validate_email(email):
            flash("Please enter a valid email address")

        #if validation succesful save to database
        else:
            save_user_to_db(first_name,last_name,email,password)
            save_logged_in_user(email_exists(email)[0])
            #validation succeeds redirect -> wall
            return redirect('/wall')
        #validation fails  redirect -> register page
        return render_template('register.html')
    else:
        return render_template('register.html')

@app.route('/wall')
def wall():
    '''
    returns a list of messages [{username: name, message: message comments: [{name, comment, time}]}]
    '''
    query = """SELECT concat(users.first_name, ' ', users.last_name) as op,
	messages.id,
    messages.message,
    date_Format(messages.created_at,"%D %M %Y") as date
    from users
    join messages
    on users.id = messages.user_id
    """
    #returns list of all messages
    messages = mysql.query_db(query)

    for message in messages:
        query = """SELECT comments.comment,
        concat(users.first_name, ' ', users.last_name) as commenter,
        date_format(comments.created_at,"%D %M %Y") as date,
        messages.id as message_id,
        comments.id as comment_id
        from messages
        join comments
        on messages.id = comments.message_id
        join users
        on comments.user_id = users.id
        where messages.id = :id
        """
        data = {
            "id": message["id"]
        }
        posts = mysql.query_db(query,data)
        message["comments"] = posts
    print messages 
    return render_template("wall.html", messages=messages)

#HELPER FUNCTIONS
def email_exists(email):
    '''
    input: email: string
    output: list [{}]
    takes in email and
    returns the results of an SQL query that gets the user with that email
    '''
    query = "SELECT email, id, first_name, last_name, salt, password FROM users WHERE email = :email"
    data = {
        "email": email
    }
    return mysql.query_db(query,data)

def save_logged_in_user(user):
    '''
    input: dictionary of 1 user
    output: none
    '''
    session["current_user_id"] = user["id"]
    session["current_user_name"] = user["first_name"]
    session["current_user_last_name"] = user["last_name"]
    session["current_user_email"] = user["email"]
    session["logged_in"] = True

def logout_user():
    '''
    set all session values to None
    '''
    session["current_user_id"] = None
    session["current_user_name"] = None
    session["current_user_last_name"] = None
    session["current_user_email"] = None
    session["logged_in"] = False

def save_user_to_db(first_name,last_name,email,password):
    """
    Takes all necessary data to create user, uses get_salt to create random salt, hashes password,
    saves data to users table
    """
    salt = get_salt()
    hashed_password = hash_password(password,salt)
    query = """INSERT into USERS (first_name, last_name, email, password, salt, created_at, updated_at)
        values (:first_name, :last_name, :email, :password, :salt, NOW(), NOW())"""
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": hashed_password,
        "salt": salt
    }
    mysql.query_db(query,data)
    print("added to database")

def get_salt():
    '''
    returns random salt
    '''
    return b2a_hex(urandom(15))

def hash_password(password,salt):
    '''
    takes password: string, salt: string
    uses md5 to created hash password
    return hashed_password: string
    '''
    return md5_new(password+salt).hexdigest()





app.run(debug=True)
