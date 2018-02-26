from flask import Flask, redirect, flash, render_template, request
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,"emails")
app.secret_key = "LasLlaves"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success')
def success():
    query = "select email_addresses.email, date_format(entry.created_at, '%m/%d/%Y %h:%i') as date, entry.id from email_addresses join entry on email_addresses.id = entry.email_addresses_id"
    data = mysql.query_db(query)
    return render_template('success.html',data=data)

@app.route('/delete/<id>')
def delete(id):
    query = "delete from entry where id = :id"
    data = {
        "id": id
    }
    mysql.query_db(query,data)
    return redirect('/success')

@app.route('/check_email',methods=["POST"])
def check_email():
    email = request.form["email"]
    query = "select * from email_addresses where email = :email"
    data = {
        "email": email
    }
    results = mysql.query_db(query,data)
    if len(results) > 0:
        flash("Email address, {}, provided was a VALID email address! Thank You".format(email),"success")
        print results
        email_id = results[0]["id"]
        query = "insert into entry (email_addresses_id, created_at) values (:email_id, NOW())"
        data = {
            "email_id": email_id
        }
        mysql.query_db(query,data)
        return redirect('/success')
    else:
        flash("Email provided was not valid","error")
        return redirect('/')
    return redirect('/')

app.run(debug=True)
