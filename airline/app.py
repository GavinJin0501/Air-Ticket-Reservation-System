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
    else:
        return redirect(url_for("search_flight"))


@app.route('/SearchFlight', methods=['GET', 'POST'])
def search_flight():
    airport_city = get_airport_and_city(conn)
    flights = []
    print(airport_city)
    if request.method == "GET":
        return render_template("public_view.html", airport_city=airport_city, flights=flights)
    elif request.method == "POST":
        source = request.form['depart']
        destination = request.form['arrive']
        date = request.form['date']

        source = source.split(" - ")
        destination = destination.split(" - ")
        # print(source, destination, date)

        src_city = source[0]
        dst_city = destination[0]
        src_airport = ""
        dst_airport = ""
        if len(source) == 2:
            src_airport = source[1]
        if len(destination) == 2:
            dst_airport = destination[1]

        flights = get_flights_by_location(conn, date, src_city, dst_city, src_airport, dst_airport)
        return render_template("public_view.html", airport_city=airport_city, flights=flights)


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
