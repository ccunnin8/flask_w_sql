from flask import Flask, redirect, flash, render_template, request
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,"mydb")
app.secret_key = "LasLlaves"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_email',methods=["POST"])
def check_email():
    email = request.form["email"]
    query = "select * from email_addresses where email = :email"
    data = {
        "email": email
    }
    results = mysql.query_db(query,data)
    if len(results) > 0:
        flash("Email provided was valid","success")
    else:
        flash("Email provided was not valid","error")
    return redirect('/')

app.run(debug=True)
