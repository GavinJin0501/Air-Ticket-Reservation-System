from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
import json
from db_utils import *

app = Flask(__name__)

app.secret_key = 'some key that you will never guess'
conn = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='air_ticket_reservation_system')


@app.route('/')
def home():
    if session.get("logged_in", False):
        if session["type"] == "customer":
            pass
        elif session["type"] == "agent":
            pass
        elif session["type"] == "airline_staff":
            pass
    return redirect(url_for("search_flight"))


@app.route('/SearchFlight', methods=['GET', 'POST'])
def search_flight():
    airport_city = get_airport_and_city(conn)
    print(airport_city)
    if request.method == "GET":
        return render_template("public_view.html", airport_city=airport_city, flights=[])
    elif request.method == "POST":
        source = request.form['depart']
        destination = request.form['arrive']
        date = request.form['date']
        print(source, destination, date)
        # get_flights_by_location(source, destination, date)
        return render_template("public_view.html", airport_city=airport_city, flights=[(1, 2, 3), (4, 5, 6)])


@app.route('/login/Customer', methods=['Get', 'Post'])
def login_customer():
    pass


@app.route('/login/Agent', methods=['Get', 'Post'])
def login_agent():
    pass


@app.route('/login/AirlineStaff', methods=['Get', 'Post'])
def login_airline_staff():
    pass


@app.route('/register/Customer', methods=['Get', 'Post'])
def register_customer():
    pass


@app.route('/register/Agent', methods=['Get', 'Post'])
def register_agent():
    pass


@app.route('/register/AirlineStaff', methods=['Get', 'Post'])
def register_airline_staff():
    pass


@app.route('/logout')
def logout():
    if not session.get("logged_in", False):
        return redirect(url_for("public_view"))
    else:
        session["logged_in"] = False
        return redirect(url_for("public_view"))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
