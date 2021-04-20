# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
from mysql_query import *
import mysql.connector


PASSWORD_HASH = "md5"


app = Flask(__name__)

conn = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='blog')


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    status = login_check(conn, username, password)
    error = None
    if status:
        session['username'] = username
        return redirect(url_for('home'))
    else:
        error = 'Invalid login or username'
        return render_template('login.html', error=error)


@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    username = request.form['username']
    password = request.form['password']

    #	if not len(password) >= 4:
    #                flash("Password length must be at least 4 characters")
    #               return redirect(request.url)

    data = register_check(conn, username)
    error = None
    if data:
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        session['username'] = username
        register_store(conn, username, password)
        flash("You are logged in")
        return render_template('index.html')


@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();
    query = "SELECT ts, blog_post FROM blog WHERE username = \'{}\' ORDER BY ts DESC"
    cursor.execute(query.format(username))
    data1 = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=username, posts=data1)


@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor()
    blog = request.form['blog']
    query = "INSERT INTO blog (blog_post, username) VALUES(\'{}\', \'{}\')"
    cursor.execute(query.format(blog, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
