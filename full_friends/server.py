from flask import Flask, redirect, render_template, flash, request
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app,"mydb")

@app.route('/')
def index():
    query = "select concat(first_name,' ',last_name) as name, age, date_format(created_at, '%M %D') as friend_since, date_format(created_at, '%Y') as year from users"
    data = mysql.query_db(query)
    return render_template('index.html',friends=data)

@app.route('/add_friend',methods=["POST"])
def add_friend():
    name = request.form['name'].split()
    if len(name) > 1:
        first_name = name[0]
        last_name = name[1]
    else:
        first_name = name[0]
        last_name = ""
    age = int(request.form['age'])
    query = "insert into users (first_name, last_name, age, created_at, updated_at) values (:first_name, :last_name, :age, NOW(), NOW())"
    data = {
        'first_name': first_name,
        'last_name': last_name,
        'age': age
    }
    mysql.query_db(query,data)
    return redirect('/')

app.run(debug=True)
