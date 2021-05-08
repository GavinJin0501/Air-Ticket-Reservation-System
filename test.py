'''
def get_customer_flight(conn, customer_email, airline_name):
    cursor = conn.cursor(prepared=True)
    query = """SELECT flight_num, departure_airport, departure_time, arrival_airport, arrival_time, status, airplane_id
               FROM purchases NATURAL JOIN ticket NATURAL JOIN flight
               WHERE customer_email = %s AND airline_name = %s"""
    print(query)
    cursor.execute(query, (customer_email, airline_name))
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        data[i] = list(data[i])
    return data


def view_reports(conn, airline_name, start_date, end_date):
    cursor = conn.cursor()
    pass


<input type="text" id = "em" name = "airline_name" placeholder="airline name" value="{{session['airline']}}" readonlys/> </br>


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
        print(month_wise)
        reports = db_utils.view_reports(conn, session["airline"], month_wise[-1][0], TODAY.strftime("%Y-%m-%d"))



<select name="status" id="status" style="font-size: 18px; height: 40px; width: 150px; text-align: center;">
                    <option value="Upcoming" style="background-color: #00fa15; text-align: center">Upcoming</option>
                    <option value="In-progress" style="background-color: #06a8ff">In-progress</option>
                    <option value="Delayed" style="background-color: #ffda06">Delayed</option>
                    <option value="Canceled" style="background-color: #ff0606">Canceled</option>
                </select>
'''