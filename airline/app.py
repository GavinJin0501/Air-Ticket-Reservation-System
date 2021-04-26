from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import datetime
import mysql.connector
import re
from db_utils import *

# App initlization:
# ======================================================================================
app = Flask(__name__)

app.secret_key = 'some key that you will never guess'
conn = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='air_ticket_reservation_system')
app.config["SEND-FILE_MAX_AGE_DEFAULT"] = 1
EMAIL_REGEX = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
# ======================================================================================


# Utility functions: 
# ======================================================================================
def is_match(stdin, pattern):
    return re.search(pattern, stdin) is not None

def logged_in_redirect():
    if session["type"] == "airline_staff":
        return redirect(url_for())
    else:
        return redirect(url_for("search_flight"))

# ======================================================================================


# App initlization:
@app.route('/')
def home():
    if session.get("logged_in", False):
        return logged_in_redirect()
    return redirect(url_for("search_flight"))


# Public view functions:
# ======================================================================================
@app.route('/SearchFlight', methods=['GET', 'POST'])
def search_flight():
    if session.get("logged_in", False) and session.get("type") == "airline_staff":
        return redirect(url_for())

    # results for autocomplete in the client side
    airport_city = get_airport_and_city(conn)
    flights = []
    # print(airport_city)
    if not session.get("logged_in"):
        identity = "guest"
        email = ""
    else:
        identity = session.get("type", "guest")
        email = session.get("email", "guest")

    if request.method == "GET":
        return render_template("public_view.html", airport_city=airport_city, flights=flights, identity=identity, email=email)
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

        # flights is a nested list, with its sublist:
        # [airline_name, flight_num, depart_airport, depart_city, depart_time,
        #  arrive_airport, arrive_city, arrive_time, price, status, plane_id]
        flights = get_flights_by_location(conn, date, src_city, dst_city, src_airport, dst_airport)
        if not flights:
            flights = ["No flights"]
        # print(flights)
        return render_template("public_view.html", airport_city=airport_city, flights=flights, identity=identity, email=email)

@app.route('/CheckStatus', methods=['GET', 'POST'])
def check_flight_status():
    if session.get("logged_in", False) and session.get("type") == "airline_staff":
        return redirect(url_for())

    if request.method == "GET":
        today = datetime.now().strftime("%Y-%m-%d")
        recent_flight_status = get_flight_status(conn, "", today, "")
        return render_template("check_status.html", status_result=recent_flight_status)
    elif request.method == "POST":
        flight_num = request.form.get("flight_num", "")
        departure_date = request.form.get("departure_date", "")
        arrival_date = request.form.get("arrival_date", "")

        flight_status_ans = get_flight_status(conn, flight_num, departure_date, arrival_date)
        if not flight_status_ans:
            flight_status_ans = ["No such a flight at the given time!"]
        print(flight_status_ans)
        return render_template("check_status.html", status_result=flight_status_ans)

@app.route('/ViewMyFlights/<string:identity>', methods=["GET"])
def view_my_flights(identity):
    if not session.get("logged_in", False):
        return redirect(url_for("home"))
    elif identity not in ["customer", "booking_agent", "airline_staff"]:
        return redirect(url_for("home"))
    elif identity != session.get("type", "guest"):
        flash("Don't try to cheat your identity!")
        return redirect(url_for("home"))

    if request.method == "GET":
        upcoming_flights = get_upcoming_flights(conn, identity, email)
        return render_template("ViewMyFlights.html", flights=upcoming_flights)

# ======================================================================================


# Login functions:
# ======================================================================================
@app.route('/login', methods=['GET'])
def login_general_page():
    if session.get("logged_in", False):
        return logged_in_redirect()
    return render_template("login_general.html")

# identity = customer/booking_agent/airline_staff
@app.route('/login/<string:identity>', methods=['GET', 'POST'])
def login_page(identity):
    if identity not in ["customer", "booking_agent", "airline_staff"]:
        return redirect(url_for("login_general_page"))
    elif session.get("logged_in", False):
        return logged_in_redirect()
    
    error = ""
    if request.method == "GET":
        return render_template("login_%s.html" % identity, error=error)
    elif request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]
        # if not is_match(email, EMAIL_REGEX):
        #     error = "Email address invalid"
        #     return render_template("login_%s.html" % identity, error=error)
        if not login_check(conn, email, password, identity):
            error = "Email address or password invalid"
            return render_template("login_%s.html" % identity, error=error)
        else:
            session["logged_in"] = True
            session["type"] = identity
            session["email"] = email
            return redirect(url_for("search_flight"))
# ======================================================================================


# Register functions:
# ======================================================================================
@app.route('/register', methods=['GET'])
def register_general_page():
    if session.get("logged_in", False):
        return logged_in_redirect()
    return render_template("register_general.html")


# identity = customer/booking_agent/airline_staff
@app.route('/register/<string:identity>', methods=['GET', 'POST'])
def register_page(identity):
    if identity not in ["customer", "booking_agent", "airline_staff"]:
        return redirect(url_for("register_general_page"))
    elif session.get("logged_in", False):
        return logged_in_redirect()
    else:
        error = ""
        if request.method == "GET":
            return render_template("register_%s.html" % identity, error=error)
        elif request.method == "POST":
            info = {"email": request.form.get("username"),
                    "password": request.form.get("password"),
                    "name": request.form.get("name"),
                    "first_name": request.form.get("first_name"),
                    "last_name": request.form.get("last_name"),
                    "building_number": request.form.get("building_number"),
                    "street": request.form.get("street"),
                    "city": request.form.get("city"),
                    "state": request.form.get("state"),
                    "phone_number": request.form.get("phone_number"),
                    "passport_number": request.form.get("passport_number"),
                    "passport_expiration": request.form.get("passport_expiration"),
                    "passport_country": request.form.get("passport_country"),
                    "date_of_birth": request.form.get("date_of_birth"),
                    "booking_agent_id": request.form.get("booking_agent_id"),
                    "airline_name": request.form.get("airline_name")}
            if not is_match(info["email"], EMAIL_REGEX):
                error = "Email address invalid"
                return render_template("register_%s.html" % identity, error=error)
            elif not register_check(conn, info["email"], identity):
                error = "Email has already been used"
                return render_template("register_%s.html" % identity, error=error)

            register_to_database(conn, info, identity)
            session["logged_in"] = True
            session["type"] = identity
            session["email"] = info["email"]
            return redirect(url_for("search_flight"))
# ======================================================================================


# Customer functions:
# ======================================================================================
# ======================================================================================

# STEPS:
# 1. Check if user is logged in
# 2. Check if his type is valid for this funciton





# Booking agent functions:
# ======================================================================================
# ======================================================================================



# Airline staff functions:
# ======================================================================================
# ======================================================================================




# Logout function:
# ======================================================================================
@app.route('/logout')
def logout():
    if not session.get("logged_in", False):
        return redirect(url_for("search_flight"))
    else:
        session["logged_in"] = False
        return redirect(url_for("search_flight"))
# ======================================================================================


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
