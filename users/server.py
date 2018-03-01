from flask import Flask, redirect, render_template, request
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,"friendsdb")

@app.route('/users')
def index():
    query = """Select id, concat(first_name," ",last_name) as name, email, date_format(created_at, "%M %D, %Y") as created_at
    from friends"""
    results = mysql.query_db(query)
    return render_template('index.html',users=results)

@app.route('/users/new')
def new():
    return render_template('add.html')

@app.route('/users/<id>/edit')
def edit(id):
    return render_template("edit.html",id=id)

@app.route('/users/<id>')
def show(id):
    query = """select id, concat(first_name, " ", last_name) as name, email, created_at as date
    from friends
    where id = :id"""
    data = {
        "id": id
    }
    user = mysql.query_db(query,data)[0]
    print user
    return render_template("user.html",id=user["id"],name=user["name"], date=user["date"], email=user["email"])

@app.route('/users/create',methods=["POST"])
def create():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    query = """insert into friends (first_name, last_name, email, created_at, updated_at)
    values (:first_name, :last_name, :email, NOW(), NOW())"""
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }
    mysql.query_db(query,data)
    return redirect('/users')

@app.route('/users/<id>/destroy')
def destroy(id):
    query = """delete from friends where id = :id"""
    data = { "id": id }
    mysql.query_db(query,data)
    return redirect('/users')

@app.route('/users/<id>',methods=["POST"])
def update(id):
    email = request.form["email"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    query = """update friends
    set first_name = :first_name, last_name = :last_name, email = :email,
    updated_at = NOW()
    where id = :id"""
    data = { "email": email, "first_name": first_name, "last_name": last_name, "id": id}
    mysql.query_db(query,data)
    return redirect('/users')

app.run(debug=True)
