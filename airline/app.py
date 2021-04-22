from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector
import re
from db_utils import *

app = Flask(__name__)

app.secret_key = 'some key that you will never guess'
conn = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='air_ticket_reservation_system')
app.config["SEND-FILE_MAX_AGE_DEFAULT"] = 1

# math standards for email, :
EMAIL_REGEX = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


def is_math(stdin, pattern):
    return re.search(pattern, stdin) is not None


def logged_in_redirect():
    if session["type"] == "customer":
        pass
    elif session["type"] == "agent":
        pass
    elif session["type"] == "airline_staff":
        pass
    return redirect()


@app.route('/')
def home():
    if not session.get("logged_in", False):
        return redirect(url_for("search_flight"))
    else:
        if session["type"] == "customer":
            pass
        elif session["type"] == "agent":
            pass
        elif session["type"] == "airline_staff":
            pass


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
        print(source, destination, date)

        src_city = source[0]
        dst_city = destination[0]
        src_airport = ""
        dst_airport = ""
        if len(source) == 2:
            src_airport = source[1]
        if len(destination) == 2:
            dst_airport = destination[1]

        # flights is a nested list, with its sublist:
        # [airline_name, flight_num, depart_airport, depart_city, depart_time,
        #  arrive_airport, arrive_city, arrive_time, price, status, plane_id]
        flights = get_flights_by_location(conn, date, src_city, dst_city, src_airport, dst_airport)
        # if not flights:
        #     flights = ["No flights"]
        # print(flights)
        return render_template("public_view.html", airport_city=airport_city, flights=flights)


@app.route('/login', methods=['Get'])
def login():
    if not session.get("logged_in", False):
        return render_template("login_general.html")
    else:
        if session["type"] == "customer":
            pass
        elif session["type"] == "agent":
            pass
        elif session["type"] == "airline_staff":
            pass


@app.route('/login/Customer', methods=['Get', 'Post'])
def login_customer():
    if not session.get("logged_in", False):
        error = ""
        if request.method == "GET":
            return render_template("login_customer.html", error=error)
        elif request.method == "POST":
            email = request.form["username"]
            password = request.form["password"]
            if not is_math(email, EMAIL_REGEX):
                error = "Email address invalid"
                return render_template("login_customer", error=error)
            if not login_check(conn, email, password, "customer"):
                error = "Email address or password invalid"
                return render_template("login_customer", error=error)
            return redirect(url_for("customer_home"))

    else:
        if session["type"] == "customer":
            pass
        elif session["type"] == "agent":
            pass
        elif session["type"] == "airline_staff":
            pass


@app.route('/login/Agent', methods=['Get', 'Post'])
def login_agent():
    if not session.get("logged_in", False):
        error = ""
        if request.method == "GET":
            return render_template("login_customer.html", error=error)
        elif request.method == "POST":
            email = request.form["username"]
            password = request.form["password"]
            if not is_math(email, EMAIL_REGEX):
                error = "Email address invalid"
                return render_template("login_customer", error=error)
            if not login_check(conn, email, password, "booking_agent"):
                error = "Email address or password invalid"
                return render_template("login_customer", error=error)
            return redirect(url_for("customer_home"))

    else:
        if session["type"] == "customer":
            pass
        elif session["type"] == "agent":
            pass
        elif session["type"] == "airline_staff":
            pass


@app.route('/login/Staff', methods=['Get', 'Post'])
def login_airline_staff():
    if not session.get("logged_in", False):
        error = ""
        if request.method == "GET":
            return render_template("login_customer.html", error=error)
        elif request.method == "POST":
            email = request.form["username"]
            password = request.form["password"]
            if not is_math(email, EMAIL_REGEX):
                error = "Email address invalid"
                return render_template("login_customer", error=error)
            if not login_check(conn, email, password, "airline_staff"):
                error = "Email address or password invalid"
                return render_template("login_customer", error=error)
            return redirect(url_for("customer_home"))

    else:
        if session["type"] == "customer":
            pass
        elif session["type"] == "agent":
            pass
        elif session["type"] == "airline_staff":
            pass


@app.route('/register/Customer', methods=['Get', 'Post'])
def register_customer():
    pass


@app.route('/register/Agent', methods=['Get', 'Post'])
def register_agent():
    pass


@app.route('/register/Staff', methods=['Get', 'Post'])
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
