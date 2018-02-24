from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'friendsdb')

@app.route('/')
def index():
    friends = mysql.query_db('SELECT * FROM friends')
    return render_template('index.html',friends=friends)

@app.route('/friends',methods=["POST"])
def create():
    query = "INSERT INTO FRIENDS (first_name, last_name, occupation, created_at, updated_at) VALUES(:first_name, :last_name, :occupation, NOW(), NOW())"
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "occupation": request.form["occupation"]
    }
    mysql.query_db(query,data)
    return redirect('/')

@app.route('/update_friend/<friend_id>', methods=["POST"])
def update(friend_id):
    query = "UPDATE friends set first_name = :first_name, last_name = :last_name, occupation = :occupation where id = :id"
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "occupation": request.form["occupation"],
        "id": friend_id
    }
    mysql.query_db(query,data)
    return redirect('/')

@app.route('/remove_friend/<friend_id>',methods=["POST"])
def delete(friend_id):
    query = "DELETE FROM friends where id = :id"
    data = {"id": friend_id }
    mysql.query_db(query,db)
    return redirect('/')

@app.route('/friends/<friend_id>')
def show(friend_id):
    query = "SELECT * FROM friends where id = :specific_id"
    data = {'specific_id': friend_id }
    friends = mysql.query_db(query,data)
    return render_template('index.html',one_friend=friends[0])


app.run(debug=True)
