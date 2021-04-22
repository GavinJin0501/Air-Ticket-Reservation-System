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

# math standards for email:
EMAIL_REGEX = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


def is_match(stdin, pattern):
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
    # else:
    #     if session["type"] == "customer":
    #         pass
    #     elif session["type"] == "agent":
    #         pass
    #     elif session["type"] == "airline_staff":
    #         pass


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
        if src_city == dst_city:
            error = "Can not travel between the same city"
            return render_template("public_view.html", airport_city=airport_city, flights=flights, error=error)
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
        return render_template("public_view.html", airport_city=airport_city, flights=flights)


@app.route('/CheckStatus')
def check_flight_status():
    pass


@app.route('/login', methods=['Get'])
def login_general_page():
    if not session.get("logged_in", False):
        return render_template("login_general.html")
    # else:
    #     if session["type"] == "customer":
    #         pass
    #     elif session["type"] == "agent":
    #         pass
    #     elif session["type"] == "airline_staff":
    #         pass


# identity = customer/booking_agent/airline_staff
@app.route('/login/<string:identity>', methods=['Get', 'Post'])
def login_page(identity):
    if identity not in ["customer", "booking_agent", "airline_staff"]:
        return redirect(url_for("login_general_page"))
    elif not session.get("logged_in", False):
        error = ""
        if request.method == "GET":
            return render_template("login_%s.html" % identity, error=error)
        elif request.method == "POST":
            email = request.form["username"]
            password = request.form["password"]
            if not is_match(email, EMAIL_REGEX):
                error = "Email address invalid"
                return render_template("login_%s.html" % identity, error=error)
            elif not login_check(conn, email, password, identity):
                error = "Email address or password invalid"
                return render_template("login_%s.html" % identity, error=error)
            else:
                session["logged_in"] = True
                session["type"] = identity
                session["email"] = email
                return redirect(url_for("search_flight"))

    # else:
    #     if session["type"] == "customer":
    #         pass
    #     elif session["type"] == "agent":
    #         pass
    #     elif session["type"] == "airline_staff":
    #         pass


@app.route('/register', methods=['Get'])
def register_general_page():
    if not session.get("logged_in", False):
        return render_template("register_general.html")
    # else:
    #     if session["type"] == "customer":
    #         pass
    #     elif session["type"] == "agent":
    #         pass
    #     elif session["type"] == "airline_staff":
    #         pass


# identity = customer/booking_agent/airline_staff
@app.route('/register/<string:identity>', methods=['Get', 'Post'])
def register_page(identity):
    if identity not in ["customer", "booking_agent", "airline_staff"]:
        return redirect(url_for("register_general_page"))
    elif not session.get("logged_in", False):
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


@app.route('/logout')
def logout():
    if not session.get("logged_in", False):
        return redirect(url_for("public_view"))
    else:
        session["logged_in"] = False
        return redirect(url_for("public_view"))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
