from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import datetime, timedelta
import mysql.connector
import re
import db_utils

# App initialization:
# ======================================================================================
app = Flask(__name__)

app.secret_key = 'some key that you will never guess'
conn = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='air_ticket_reservation_system')
app.config["SEND-FILE_MAX_AGE_DEFAULT"] = 1
EMAIL_REGEX = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
MONTH_EN = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}


# ======================================================================================


# Utility functions: 
# ======================================================================================
def is_match(stdin, pattern):
    return re.search(pattern, stdin) is not None


def logged_in_redirect():
    if session["type"] == "airline_staff":
        return redirect(url_for("view_my_flights"))
    else:
        return redirect(url_for("search_flight"))


def get_each_month(month_wise, start_year, start_month, end_year, end_month, start_date, end_date):
    if start_year == end_year and start_month == end_month:
        month_wise.append([start_date, end_date, 0])
    else:
        if start_month == 12:
            start_year += 1
            start_month = 0
        month_wise.append([start_date, "%d-%02d-01" % (start_year, start_month + 1), 0])
        start_month += 1
        while start_year <= end_year:
            if start_year == end_year:
                if start_month >= end_month:
                    break
                else:
                    month_wise.append(
                        ["%d-%02d-01" % (start_year, start_month), "%d-%02d-01" % (start_year, start_month + 1), 0])
            else:
                if start_month == 12:
                    month_wise.append(["%d-%02d-01" % (start_year, start_month), "%d-%02d-01" % (start_year + 1, 1), 0])
                    start_year += 1
                    start_month = 0
                else:
                    month_wise.append(
                        ["%d-%02d-01" % (start_year, start_month), "%d-%02d-01" % (start_year, start_month + 1), 0])
            start_month += 1
        month_wise.append(["%d-%02d-01" % (end_year, end_month), end_date, 0])


# ======================================================================================


# App initialization:
@app.route('/')
def home():
    if session.get("logged_in", False):
        return logged_in_redirect()
    return redirect(url_for("search_flight"))


# Public view functions:
# ======================================================================================
@app.route('/SearchFlight', methods=['GET', 'POST'])
def search_flight():
    # if session.get("logged_in", False) and session.get("type") == "airline_staff":
    #     return redirect(url_for("view_my_flights"))

    # results for autocomplete in the client side
    airport_city = db_utils.get_airport_and_city(conn)
    flights = []
    # print(airport_city)

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

        # flights is a nested list, with its sublist:
        # [airline_name, flight_num, depart_airport, depart_city, depart_time,
        #  arrive_airport, arrive_city, arrive_time, price, status, plane_id]
        flights = db_utils.get_flights_by_location(conn, date, src_city, dst_city, src_airport, dst_airport)
        if not flights:
            flights = ["No flights"]
        # print(flights)
        return render_template("public_view.html", airport_city=airport_city, flights=flights)


@app.route('/CheckStatus', methods=['GET', 'POST'])
def check_flight_status():
    # if session.get("logged_in", False) and session.get("type") == "airline_staff":
    #     return redirect(url_for("view_my_flights"))

    if request.method == "GET":
        today = datetime.now().strftime("%Y-%m-%d")
        # today = "2021-05-01"
        recent_flight_status = db_utils.get_flight_status(conn, "", today, "")
        print(recent_flight_status)
        return render_template("check_status.html", status=False, error="", status_result=recent_flight_status)
    elif request.method == "POST":
        flight_num = request.form.get("flight_num", "")
        departure_date = request.form.get("departure_date", "")
        arrival_date = request.form.get("arrival_date", "")
        print(flight_num, departure_date, arrival_date)

        flight_status_ans = db_utils.get_flight_status(conn, flight_num, departure_date, arrival_date)
        error = ""
        status = True
        if not flight_status_ans:
            error = "No such a flight at the given time!"
            status = False
        # print(flight_status_ans)
        return render_template("check_status.html", status=status, error=error, status_result=flight_status_ans)


@app.route('/ViewMyFlights', methods=["GET", "POST"])
def view_my_flights():
    if not session.get("logged_in", False):
        return redirect(url_for("home"))

    identity = session.get("type", "guest")
    if request.method == "GET":
        upcoming_flights = db_utils.get_upcoming_flights(conn, identity, session["email"])
        print(upcoming_flights)
        return render_template("view_my_flights.html", flights=upcoming_flights)
    elif request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        print(start_date, end_date)

        flights = db_utils.get_time_flights(conn, identity, session["email"], start_date, end_date)
        return render_template("view_my_flights.html", flights=flights)


@app.route('/CustomerNames/<flight_num>', methods=["GET"])
def view_flight_customers(flight_num):
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        # ["Airline", "Flight", "Depart airport", "Depart city", "Depart time", "Arrive airport", "Arrive city", "Arrive time", "Price", "Status", "Airplane"];
        clicked_flight = db_utils.get_specified_flight(conn, session["airline"], flight_num)
        customer_info = db_utils.get_flight_customers(conn, session["airline"], flight_num)
        print(clicked_flight, customer_info)
        return render_template("CustomerNames.html", clicked_flight=clicked_flight, customer_info=customer_info)


@app.route('/purchase/<airline_name>/<flight_num>', methods=["GET"])
def purchase(airline_name, flight_num):
    if not session.get("logged_in", False):
        return redirect(url_for("login_purchase", airline_name=airline_name, flight_num=flight_num))
    elif session.get("type", "guest") == "airline_staff":
        return redirect(url_for("view_my_flights"))

    if request.method == "GET":
        return redirect(url_for("purchase_confirm", airline_name=airline_name, flight_num=flight_num))


@app.route('/purchase/confirm/<airline_name>/<flight_num>', methods=["GET", "POST"])
def purchase_confirm(airline_name, flight_num):
    if not session.get("logged_in", False):
        return redirect(url_for("login_purchase", airline_name=airline_name, flight_num=flight_num))
    elif session.get("type", "guest") == "airline_staff":
        return redirect(url_for("view_my_flights"))

    if request.method == "GET":
        # print(airline_name, flight_num)
        return render_template("purchase_confirm.html", email=session["email"], airline_name=airline_name,
                               flight_num=flight_num)
    elif request.method == "POST":
        # print(airline_name, flight_num)
        identity = session["type"]
        if identity == "customer":
            customer_email = session["email"]
            agent_email = ""
        else:
            customer_email = request.form.get("customer_email")
            agent_email = session["email"]

        status, error = db_utils.purchase_ticket(conn, identity, customer_email, agent_email, airline_name, flight_num)
        if status:
            print("purchase success")
            return redirect(url_for("view_my_flights"))
        else:
            print("purchase fail")
            return render_template("purchase_confirm.html", email=session["email"], airline_name=airline_name,
                                   flight_num=flight_num, error=error)


@app.route('/purchase/login/<airline_name>/<flight_num>', methods=["GET", "POST"])
def login_purchase(airline_name, flight_num):
    if session.get("logged_in", False):
        return redirect(url_for("home"))

    error = ""
    if request.method == "GET":
        return render_template("login_purchase.html", error=error, airline_name=airline_name, flight_num=flight_num)
    elif request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]
        identity = "customer"
        if not db_utils.login_check(conn, email, password, identity):
            error = "Email address or password invalid"
            return render_template("login_purchase.html", error=error, airline_name=airline_name, flight_num=flight_num)
        else:
            session["logged_in"] = True
            session["type"] = identity
            session["email"] = email
            return redirect(url_for("purchase_confirm", airline_name=airline_name, flight_num=flight_num))


@app.route('/TrackMySpending', methods=["GET", "POST"])
def track_my_spending():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "customer":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    total_amount = 0
    month_wise = []  # List of lists: [[start_date, end_date, money], .......]

    if request.method == "GET":
        TODAY = datetime.today()
        PAST = (TODAY - timedelta(days=365))
        THIS_YEAR, PAST_YEAR, THIS_MONTH = TODAY.year, TODAY.year - 1, TODAY.month
        month_wise.append(["%d-%02d-01" % (THIS_YEAR, THIS_MONTH), TODAY.strftime("%Y-%m-%d"), 0])
        for i in range(1, 6):
            if THIS_MONTH - i > 0:
                temp = ["%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i), "%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i + 1), 0]
            elif THIS_MONTH - i + 1 > 0:
                temp = ["%d-%02d-01" % (PAST_YEAR, 12 + (THIS_MONTH - i)),
                        "%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i + 1), 0]
            else:
                temp = ["%d-%02d-01" % (PAST_YEAR, 12 + (THIS_MONTH - i)),
                        "%d-%02d-01" % (THIS_YEAR, 12 + (THIS_MONTH - i + 1)), 0]
            month_wise.append(temp)

        total_amount = db_utils.get_my_spendings_total_amount(conn, session["email"], PAST.strftime("%Y-%m-%d"),
                                                              TODAY.strftime("%Y-%m-%d"))
        my_spendings = db_utils.get_my_spendings_certain_range(conn, session["email"], month_wise[-1][0],
                                                               month_wise[0][1])
        print(my_spendings)
        print(total_amount)
        print(month_wise)

        for i in my_spendings:
            for j in month_wise:
                if j[0] < i[0] <= j[1]:
                    j[2] += i[1]
                    break

        for i in range(len(month_wise)):
            month_wise[i] = [month_wise[i][0] + " - " + month_wise[i][1], month_wise[i][2]]

        return render_template("track_my_spending.html", total_amount=total_amount, month_wise=month_wise)

    elif request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        # print(start_date, end_date)
        start_year, start_month = int(start_date[:4]), int(start_date[5:7])
        end_year, end_month = int(end_date[:4]), int(end_date[5:7])

        get_each_month(month_wise, start_year, start_month, end_year, end_month, start_date, end_date)
        print(month_wise)

        total_amount = db_utils.get_my_spendings_total_amount(conn, session["email"], start_date, end_date)
        my_spendings = db_utils.get_my_spendings_certain_range(conn, session["email"], start_date, end_date)
        print(total_amount)

        for i in my_spendings:
            for j in month_wise:
                if j[0] < i[0] <= j[1]:
                    j[2] += i[1]
                    break

        for i in range(len(month_wise)):
            month_wise[i] = [month_wise[i][0] + " -> " + month_wise[i][1], month_wise[i][2]]

        return render_template("track_my_spending.html", total_amount=total_amount, month_wise=month_wise)


@app.route('/ViewMyCommission', methods=["GET", "POST"])
def view_my_commission():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "booking_agent":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    TODAY = datetime.today()
    if request.method == "GET":
        start_date = (TODAY - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = TODAY.strftime("%Y-%m-%d")
        my_commission, all_commission = db_utils.get_my_commission(conn, session["email"], start_date, end_date)
        print(my_commission, all_commission)
        return render_template("ViewMyCommission.html", my_commission=my_commission, all_commission=all_commission)
    elif request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        my_commission, all_commission = db_utils.get_my_commission(conn, session["email"], start_date, end_date)
        print(my_commission, all_commission)
        return render_template("ViewMyCommission.html", my_commission=my_commission, all_commission=all_commission)


@app.route('/ViewTopCustomers', methods=["GET"])
def view_top_customers():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "booking_agent":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        most_tickets, most_commission = db_utils.top_customers(conn, email=session["email"])
        print(most_tickets, most_commission)
        return render_template("ViewTopCustomers.html", most_tickets=most_tickets, most_commission=most_commission)


@app.route('/CreateNewFlights', methods=["GET", "POST"])
def create_new_flights():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("CreateNewFlights.html", status=False, error="")
    elif request.method == "POST":
        info = {"airline_name": request.form["airline_name"],
                "flight_num": request.form["flight_num"],  # no repetitive check
                "departure_airport": request.form["departure_airport"],  # have check
                "departure_time": request.form["departure_time"],
                "arrival_airport": request.form["arrival_airport"],  # have check
                "arrival_time": request.form["arrival_time"],
                "price": request.form["price"],
                "status": request.form.get("status"),
                "plane_id": request.form["plane_id"],  # have check
                }
        status, error = db_utils.create_new_flight(conn, info)
        return render_template("CreateNewFlights.html", status=status, error=error)


@app.route('/ChangeFlightStatus', methods=["GET", "POST"])
def change_status_of_flight():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("ChangeFlightStatus.html", status=False, error="")
    elif request.method == "POST":
        flight_num = request.form["flight_num"]
        new_status = request.form.get("status")
        status, error = db_utils.change_flight_status(conn, flight_num, new_status, session["airline"])
        return render_template("ChangeFlightStatus.html", status=status, error=error)


@app.route('/AddAirplane', methods=["GET", "POST"])
def add_airplane():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("AddAirplane.html", status=False, error="")
    elif request.method == "POST":
        airplane_id = request.form["airplane_id"]
        seats = request.form["seats"]

        return redirect(url_for("add_airplane_confirmation", airplane_id=airplane_id, seats=seats))


@app.route('/AddAirplane/Confirmation/<airplane_id>/<seats>', methods=["GET", "POST"])
def add_airplane_confirmation(airplane_id, seats):
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    planes = db_utils.get_airplanes(conn, session["airline"])
    if request.method == "GET":
        print(airplane_id, seats)
        return render_template("AirplaneConfirmation.html", airplane_id=airplane_id, seats=seats, planes=planes)
    elif request.method == "POST":
        if not seats.isdigit():
            status = False
            error = "Seats should be integer"
        else:
            status, error = db_utils.add_airplane(conn, session["airline"], airplane_id, seats)

        if not status:
            return render_template("AirplaneConfirmation.html", status=status, error=error, airplane_id=airplane_id,
                                   seats=seats, planes=planes)
        return redirect(url_for("home"))


@app.route('/AddAirport', methods=["GET", "POST"])
def add_airport():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("AddAirport.html", status=False, error="")
    elif request.method == "POST":
        airport_name = request.form["airport_name"]
        airport_city = request.form["airport_city"]

        status, error = db_utils.add_airport(conn, airport_name, airport_city)
        return render_template("AddAirport.html", status=status, error=error)


@app.route('/ViewAllBookingAgent', methods=["GET"])
def view_all_booking_agent():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        ticket_month, ticket_year, commission_year = db_utils.view_booking_agents(conn)
        return render_template("view_all_booking_agent.html", ticket_month=ticket_month, ticket_year=ticket_year,
                               commission_year=commission_year)


@app.route('/ViewFrequentCustomers', methods=["GET", "POST"])
def view_frequent_customers():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    start_date = datetime.today().strftime("%Y-%m-%d")
    end_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    most_customer, others = db_utils.view_most_frequent_customer(conn, end_date, start_date, session["airline"])
    print(most_customer, others)
    if request.method == "GET":
        return render_template("ViewFrequentCustomers.html", most_customer=most_customer, others=others)
    elif request.method == "POST":
        customer_email = request.form["customer_email"]
        customer_flights = db_utils.get_customer_flight(conn, customer_email, session["airline"])
        return render_template("ViewFrequentCustomers.html", most_customer=most_customer, others=others,
                               customer_flights=customer_flights)


@app.route('/ViewReports', methods=["GET", "POST"])
def view_reports():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    month_wise = []

    if request.method == "GET":
        TODAY = datetime.today()
        THIS_YEAR, PAST_YEAR, THIS_MONTH = TODAY.year, TODAY.year - 1, TODAY.month
        month_wise.append(["%d-%02d-01" % (THIS_YEAR, THIS_MONTH), TODAY.strftime("%Y-%m-%d"), 0])
        for i in range(1, 6):
            if THIS_MONTH - i > 0:
                temp = ["%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i), "%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i + 1), 0]
            elif THIS_MONTH - i + 1 > 0:
                temp = ["%d-%02d-01" % (PAST_YEAR, 12 + (THIS_MONTH - i)),
                        "%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i + 1), 0]
            else:
                temp = ["%d-%02d-01" % (PAST_YEAR, 12 + (THIS_MONTH - i)),
                        "%d-%02d-01" % (THIS_YEAR, 12 + (THIS_MONTH - i + 1)), 0]
            month_wise.append(temp)

        reports = db_utils.view_reports(conn, session["airline"], month_wise[-1][0], TODAY.strftime("%Y-%m-%d"))
        for i in reports:
            for j in month_wise:
                if j[0] < i[1] <= j[1]:
                    j[2] += 1
                    break
        print(reports)
        print(month_wise)
        for i in range(len(month_wise)):
            month_wise[i] = [month_wise[i][0] + " -> " + month_wise[i][1], month_wise[i][2]]

        return render_template("ViewReports.html", month_wise=month_wise)

    elif request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        start_year, start_month = int(start_date[:4]), int(start_date[5:7])
        end_year, end_month = int(end_date[:4]), int(end_date[5:7])

        get_each_month(month_wise, start_year, start_month, end_year, end_month, start_date, end_date)

        reports = db_utils.view_reports(conn, session["airline"], start_date, end_date)
        for i in reports:
            for j in month_wise:
                if j[0] < i[1] <= j[1]:
                    j[2] += 1
                    break
        print(reports)
        print(month_wise)
        for i in range(len(month_wise)):
            month_wise[i] = [month_wise[i][0] + " -> " + month_wise[i][1], month_wise[i][2]]
        return render_template("ViewReports.html", month_wise=month_wise)


@app.route('/ComparisonOfRevenueEarned', methods=["GET", "POST"])
def compare_of_revenue_earned():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        TODAY = datetime.today()
        LAST_MONTH = TODAY - timedelta(days=30)
        LAST_YEAR = TODAY - timedelta(days=365)

        direct_sales_month = db_utils.get_airline_sales(conn, LAST_MONTH.strftime("%Y-%m-%d"),
                                                        TODAY.strftime("%Y-%m-%d"), session["airline"], "direct")
        indirect_sales_month = db_utils.get_airline_sales(conn, LAST_MONTH.strftime("%Y-%m-%d"),
                                                          TODAY.strftime("%Y-%m-%d"), session["airline"], "indirect")

        direct_sales_year = db_utils.get_airline_sales(conn, LAST_YEAR.strftime("%Y-%m-%d"),
                                                       TODAY.strftime("%Y-%m-%d"), session["airline"], "direct")
        indirect_sales_year = db_utils.get_airline_sales(conn, LAST_YEAR.strftime("%Y-%m-%d"),
                                                         TODAY.strftime("%Y-%m-%d"), session["airline"], "indirect")

        return render_template("ComparisonOfRevenueEarned.html", status="GET", direct_sales_month=direct_sales_month,
                               indirect_sales_month=indirect_sales_month, direct_sales_year=direct_sales_year,
                               indirect_sales_year=indirect_sales_year, direct_sales_specific=[[0]],
                               indirect_sales_specific=[[0]])

    elif request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form.get("end_date", datetime.today().strftime("%Y-%m-%d"))

        print(start_date, "-", end_date, "-")
        direct_sales_specific = db_utils.get_airline_sales(conn, start_date, end_date, session["airline"], "direct")
        indirect_sales_specific = db_utils.get_airline_sales(conn, start_date, end_date, session["airline"], "indirect")

        print(direct_sales_specific, indirect_sales_specific)

        return render_template("ComparisonOfRevenueEarned.html", status="POST", direct_sales_month=[[0]],
                               indirect_sales_month=[[0]], direct_sales_year=[[0]], indirect_sales_year=[[0]],
                               direct_sales_specific=direct_sales_specific,
                               indirect_sales_specific=indirect_sales_specific)


@app.route('/ViewTopDestinations', methods=["GET", "POST"])
def view_top_destinations():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))
    elif session.get("type", "guest") != "airline_staff":
        flash("You don't have the authority to do so!")
        return redirect(url_for("home"))

    if request.method == "GET":
        TODAY = datetime.today()
        LAST_3_MONTH = TODAY - timedelta(days=30 * 3)
        LAST_YEAR = TODAY - timedelta(days=365)

        top_three_month = db_utils.get_top_destinations(conn, LAST_3_MONTH.strftime("%Y-%m-%d"),
                                                        TODAY.strftime("%Y-%m-%d"), session["airline"])
        top_last_year = db_utils.get_top_destinations(conn, LAST_YEAR.strftime("%Y-%m-%d"), TODAY.strftime("%Y-%m-%d"),
                                                      session["airline"])

        return render_template("ViewTopDestinations.html", status="GET", top_three_month=top_three_month,
                               top_last_year=top_last_year, top_specified=[["", 0]])

    elif request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        print(start_date, end_date)
        top_specified = db_utils.get_top_destinations(conn, start_date, end_date, session["airline"])
        return render_template("ViewTopDestinations.html", status="POST", top_three_month=[["", 0]],
                               top_last_year=[["", 0]], top_specified=top_specified)


@app.route('/Changeinfo', methods=["GET", "POST"])
def change_info():
    if not session.get("logged_in", False):
        flash("Don't cheat! Login first!")
        return redirect(url_for("home"))

    info = db_utils.get_user_info(conn, session["type"], session["email"])
    if request.method == "GET":
        return render_template("ChangeInfo_%s.html" % session["type"], info=info, error="")
    elif request.method == "POST":
        finfo = {"email": request.form.get("username"),
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
                 "booking_agent_id": request.form.get("booking_agent_id")
                 }
        identity = session["type"]
        if not is_match(finfo["email"], EMAIL_REGEX):
            error = "Email address invalid"
            return render_template("ChangeInfo_%s.html" % session["type"], info=info, error=error)

        if identity == "booking_agent":
            old_id = info[1]
        else:
            old_id = ""
        status, error = db_utils.update_user_info(conn, identity, finfo, session["email"], old_id)

        if not status:
            return render_template("ChangeInfo_%s.html" % session["type"], info=info, error=error)
        session["email"] = finfo["email"]
        return redirect(url_for("home"))


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
        if not db_utils.login_check(conn, email, password, identity):
            error = "Email address or password invalid"
            return render_template("login_%s.html" % identity, error=error)
        else:
            session["logged_in"] = True
            session["type"] = identity
            session["email"] = email
            if identity == "airline_staff":
                session["airline"] = db_utils.airline_staff_initialization(conn, email)
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
                    "airline_name": request.form.get("airline_name")
                    }
            if not is_match(info["email"], EMAIL_REGEX):
                error = "Email address invalid"
                return render_template("register_%s.html" % identity, error=error)

            status, error = db_utils.register_check(conn, info, identity)
            if not status:
                return render_template("register_%s.html" % identity, error=error)

            db_utils.register_to_database(conn, info, identity)
            session["logged_in"] = True
            session["type"] = identity
            session["email"] = info["email"]
            if identity == "airline_staff":
                session["airline"] = info["airline_name"]
            return redirect(url_for("search_flight"))


# ======================================================================================


# Logout function:
# ======================================================================================
@app.route('/logout')
def logout():
    if session.get("logged_in", False):
        session["logged_in"] = False
    return redirect(url_for("home"))


# ======================================================================================


# Error page:
# ======================================================================================
# @app.errorhandler(404)
# def not_found(e):
#     return render_template("not_found.html"), 404


# ======================================================================================

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
