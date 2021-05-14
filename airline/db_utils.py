from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

PASSWORD_HASH = "md5"


def get_airport_and_city(conn):
    data1 = []
    data2 = []
    cursor = conn.cursor()
    cursor.callproc("GetAirportWithCity")
    for result in cursor.stored_results():
        data1 = result.fetchall()
    cursor.callproc("GetUniqueAirportCity")
    for result in cursor.stored_results():
        data2 = result.fetchall()
    cursor.close()
    for i in range(len(data1)):
        data1[i] = data1[i][0] + " - " + data1[i][1]
    for i in range(len(data2)):
        data2[i] = data2[i][0]
    data2 += data1
    data2.sort()
    # print(data2)
    return data2


def get_airplanes(conn, airline_name):
    cursor = conn.cursor(prepared=True)
    query = """SELECT * FROM airplane WHERE airline_name = %s"""
    cursor.execute(query, (airline_name,))
    data = cursor.fetchall()
    cursor.close()
    return data


def get_flights_by_location(conn, date, src_city, dst_city, src_airport="", dst_airport=""):
    cursor = conn.cursor(prepared=True)
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id 
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name)
               WHERE DATE(F.departure_time) = %s AND F.status = 'Upcoming' AND SRC.airport_city = %s AND DST.airport_city= %s AND (F.departure_airport = %s OR %s = '') AND (F.arrival_airport = %s OR %s = '')
               ORDER BY departure_time
             """
    cursor.execute(query, (date, src_city, dst_city, src_airport, src_airport, dst_airport, dst_airport))
    data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][4] = data[i][4].strftime("%Y-%m-%d %H:%M:%S")
        data[i][7] = data[i][7].strftime("%Y-%m-%d %H:%M:%S")
        data[i][8] = int(data[i][8])

    return data


def login_check(conn, username, password, identity):
    cursor = conn.cursor(prepared=True)
    query = """SELECT password FROM %s WHERE """ % identity
    if identity == "airline_staff":
        query += """username = %s"""
    else:
        query += """email = %s"""
    cursor.execute(query, (username.replace("\'", "\'\'"),))
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return False
    return check_password_hash(data[0][0], password)


def airline_staff_initialization(conn, email):
    cursor = conn.cursor(prepared=True)
    query = """SELECT airline_name FROM airline_staff WHERE username = %s"""
    cursor.execute(query, (email,))
    data = cursor.fetchall()
    cursor.close()
    return data[0][0]


def register_check(conn, info, identity):
    cursor = conn.cursor(prepared=True)
    if identity == "airline_staff":
        query = """SELECT airline_name FROM airline WHERE airline_name = %s"""
        cursor.execute(query, (info["airline_name"],))
        data = cursor.fetchall()
        if not data:
            cursor.close()
            return False, "No such airline"
        query = "SELECT username FROM %s" % identity
        query += " WHERE username = %s"
        cursor.execute(query, (info["email"].replace("\'", "\'\'"),))
        data = cursor.fetchall()
        cursor.close()
        if data:
            return False, "Email has already been used"
        else:
            return True, ""
    elif identity == "booking_agent":
        query = "SELECT email FROM %s" % identity
        query += " WHERE email = %s"
        cursor.execute(query, (info["email"].replace("\'", "\'\'"),))
        data = cursor.fetchall()
        if data:
            cursor.close()
            return False, "Email has already been used"
        query = "SELECT email FROM %s" % identity
        query += " WHERE booking_agent_id = %s"
        cursor.execute(query, (info["booking_agent_id"].replace("\'", "\'\'"),))
        data = cursor.fetchall()
        if data:
            cursor.close()
            return False, "Agent id has already been used"
        return True, ""
    else:
        query = "SELECT email FROM %s" % identity
        query += " WHERE email = %s"
        cursor.execute(query, (info["email"].replace("\'", "\'\'"),))
        data = cursor.fetchall()
        cursor.close()
        if data:
            return False, "Email has already been used"
        return True, ""


def register_to_database(conn, info, identity):
    cursor = conn.cursor(prepared=True)
    query = """INSERT INTO %s""" % identity
    if identity == "customer":
        query += """ VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
        cursor.execute(query, (info["email"].replace("\'", "\'\'"), info["name"].replace("\'", "\'\'"),
                               generate_password_hash(info["password"], PASSWORD_HASH), info["building_number"],
                               info["street"].replace("\'", "\'\'"), info["city"].replace("\'", "\'\'"), info["state"],
                               info["phone_number"], info["passport_number"],
                               info["passport_expiration"], info["passport_country"], info["date_of_birth"]))
    elif identity == "booking_agent":
        query += " VALUES (%s, %s, %s)"
        cursor.execute(query, (info["email"].replace("\'", "\'\'"),
                               generate_password_hash(info["password"], PASSWORD_HASH), info["booking_agent_id"]))
    else:
        query += """ VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (info["email"].replace("\'", "\'\'"),
                               generate_password_hash(info["password"], PASSWORD_HASH),
                               info["first_name"].replace("\'", "\'\'"), info["last_name"].replace("\'", "\'\'"),
                               info["date_of_birth"], info["airline_name"]))
    conn.commit()
    cursor.close()
    return


def get_flight_status(conn, flight_num, departure_date, arrival_date):
    cursor = conn.cursor(prepared=True)
    query = """SELECT airline_name, flight_num, status, airport_city, departure_time
                FROM flight JOIN airport ON (flight.arrival_airport = airport.airport_name)
                WHERE (flight_num = %s OR %s = '') AND 
                      (DATE(departure_time) = %s OR %s = '') AND 
                      (DATE(arrival_time) = %s OR %s = '')"""
    cursor.execute(query, (flight_num, flight_num, departure_date, departure_date, arrival_date, arrival_date))
    data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][-1] = data[i][-1].strftime("%Y-%m-%d %H:%M:%S")

    return data


def get_upcoming_flights(conn, identity, email):
    next_thirty_days = (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    cursor = conn.cursor(prepared=True)
    email = email.replace("\'", "\'\'")
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name) 
               WHERE status = 'Upcoming' AND """
    if identity == "airline_staff":
        query += """DATE(departure_time) <= \'%s\' AND """ % next_thirty_days
        query += """ airline_name IN (
                        SELECT airline_name
                        FROM airline_staff
                        WHERE username = %s
        )"""
    elif identity == "customer":
        query += """ flight_num IN (
                        SELECT flight_num
                        FROM purchases NATURAL JOIN ticket
                        WHERE customer_email = %s
        )"""
    else:
        query += """ flight_num IN (
                        SELECT flight_num
                        FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent
                        WHERE email =  %s
        )"""

    # print("get upcoming flights query is:\n", query % email)
    cursor.execute(query, (email,))
    data = cursor.fetchall()
    cursor.close()

    # need to pre-process the data!!!!
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][4] = data[i][4].strftime("%Y-%m-%d %H:%M:%S")
        data[i][7] = data[i][7].strftime("%Y-%m-%d %H:%M:%S")
        data[i][8] = int(data[i][8])
    return data


def get_time_flights(conn, identity, email, start_date, end_date, src_city, dst_city, src_airport, dst_airport):
    cursor = conn.cursor(prepared=True)
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name)
               WHERE 
            """

    if identity == "airline_staff":
        query += """ airline_name IN (
                        SELECT airline_name
                        FROM airline_staff
                        WHERE username = %s
        )"""
    elif identity == "customer":
        query += """ flight_num IN (
                        SELECT flight_num
                        FROM purchases NATURAL JOIN ticket
                        WHERE customer_email = %s
        )"""
    else:
        query += """ flight_num IN (
                        SELECT flight_num
                        FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent
                        WHERE email = %s
        )"""

    query += """ AND (DATE(departure_time) >= %s OR %s = '') AND (DATE(departure_time) <= %s OR %s = '') 
                 AND (SRC.airport_city = %s OR %s = '') AND (DST.airport_city = %s OR %s = '') 
                 AND (departure_airport = %s OR %s = '') AND (arrival_airport = %s OR %s = '') 
                 ORDER BY departure_time
             """
    cursor.execute(query, (email, start_date, start_date, end_date, end_date, src_city, src_city, dst_city, dst_city, src_airport, src_airport, dst_airport, dst_airport))
    data = cursor.fetchall()
    cursor.close()

    # need to pre-process the data!!!!
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][4] = data[i][4].strftime("%Y-%m-%d %H:%M:%S")
        data[i][7] = data[i][7].strftime("%Y-%m-%d %H:%M:%S")
        data[i][8] = int(data[i][8])
    return data


def get_specified_flight(conn, airline_name, flight_num):
    cursor = conn.cursor(prepared=True)
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name) 
               WHERE airline_name = %s AND flight_num = %s
            """
    cursor.execute(query, (airline_name, flight_num))
    data = cursor.fetchall()
    cursor.close()

    data[0] = list(data[0])
    data[0][4] = data[0][4].strftime("%Y-%m-%d %H:%M:%S")
    data[0][7] = data[0][7].strftime("%Y-%m-%d %H:%M:%S")
    data[0][8] = int(data[0][8])
    return data


def purchase_ticket(conn, identity, customer_email, agent_email, airline_name, flight_num):
    cursor = conn.cursor(prepared=True)
    query = """SELECT *
                   FROM flight
                   WHERE airline_name = %s AND flight_num = %s AND status = 'Upcoming' AND departure_time > %s"""
    cursor.execute(query, (airline_name, flight_num, datetime.today().strftime("%Y-%m-%d")))
    check_flight = cursor.fetchall()
    if not check_flight:
        cursor.close()
        return False, "Don't cheat! Can't buy this flight!"

    query = """SELECT COUNT(ticket_id) 
               FROM ticket 
               WHERE flight_num = %s"""
    # print(query)
    cursor.execute(query, (flight_num,))
    ticket_num = cursor.fetchall()
    ticket_num = ticket_num[0][0] if ticket_num else 0
    query = """SELECT seats 
               FROM airplane NATURAL JOIN flight 
               WHERE flight_num = %s"""
    # print(query)
    cursor.execute(query, (flight_num,))
    seat_num = cursor.fetchall()
    seat_num = seat_num[0][0] if seat_num else 0
    # print(ticket_num, seat_num)
    if ticket_num >= seat_num:
        cursor.close()
        return False, "No ticket! This flight is full!"

    query = """SELECT * FROM customer WHERE email = %s"""
    cursor.execute(query, (customer_email,))
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Customer does not exists!"

    ticket_id = flight_num[:2] + datetime.now().strftime("%Y%m%d%H%M%S")
    today = datetime.today().strftime("%Y-%m-%d")
    query = """INSERT INTO ticket
               VALUES (%s, %s, %s)"""
    cursor.execute(query, (ticket_id, airline_name, flight_num))
    # conn.commit()

    if identity == "customer":
        query = """INSERT INTO purchases
                   VALUES (%s, %s, NULL, %s)"""
        t = (ticket_id, customer_email, today)
    else:
        query = """SELECT booking_agent_id
                   FROM booking_agent
                   WHERE email = %s"""
        cursor.execute(query, (agent_email,))
        agent_id = cursor.fetchall()[0][0]
        query = """INSERT INTO purchases
                   VALUES (%s, %s, %s, %s)"""
        t = (ticket_id, customer_email, agent_id, today)
    cursor.execute(query, t)
    conn.commit()
    cursor.close()
    return True, ""


def get_my_spendings_total_amount(conn, email, start_date, end_date):
    cursor = conn.cursor(prepared=True)
    query = """SELECT SUM(price)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN flight
               WHERE customer_email = %s AND purchase_date BETWEEN %s AND %s
            """
    cursor.execute(query, (email, start_date, end_date))
    data = cursor.fetchall()
    cursor.close()

    if data[0][0] == None:
        return 0
    else:
        return data[0][0]


def get_my_spendings_certain_range(conn, email, start_date, end_date):
    cursor = conn.cursor(prepared=True)
    query = """SELECT purchase_date, price
                FROM ticket NATURAL JOIN purchases NATURAL JOIN flight
                WHERE customer_email = %s AND purchase_date BETWEEN %s AND %s
            """
    # print(query)
    cursor.execute(query, (email, start_date, end_date))
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][0] = data[i][0].strftime("%Y-%m-%d")
        data[i][1] = int(data[i][1])
    return data


def get_my_commission(conn, email, start_date, end_date):
    cursor = conn.cursor(prepared=True)
    query = """SELECT SUM(price) * 0.1, COUNT(ticket_id), SUM(price) * 0.1 / COUNT(ticket_id)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
               WHERE email = %s AND (purchase_date >= %s OR %s = '') AND (purchase_date <= %s OR %s = '')
            """
    cursor.execute(query, (email, start_date, start_date, end_date, end_date))
    my_commission = cursor.fetchall()

    query = """SELECT SUM(price) * 0.1, COUNT(ticket_id), SUM(price) * 0.1 / COUNT(ticket_id)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
               WHERE email != %s AND (purchase_date >= %s OR %s = '') AND (purchase_date <= %s OR %s = '')
            """
    # print(query)
    cursor.execute(query, (email, start_date, start_date, end_date, end_date))
    all_commission = cursor.fetchall()
    cursor.close()

    if my_commission[0][0] == None:
        my_commission = [(0, 0, 0)]
    if all_commission[0][0] == None:
        all_commission = [(0, 0, 0)]

    for i in range(len(my_commission)):
        my_commission[i] = list(my_commission[i])
        my_commission[i][0] = float(my_commission[i][0])
        my_commission[i][1] = int(my_commission[i][1])
        my_commission[i][2] = float(my_commission[i][2])
        all_commission[i] = list(all_commission[i])
        all_commission[i][0] = float(all_commission[i][0])
        all_commission[i][1] = int(all_commission[i][1])
        all_commission[i][2] = float(all_commission[i][2])

    return my_commission, all_commission


def top_customers(conn, email):
    six_month_before = (datetime.today() - timedelta(days=6 * 31)).strftime("%Y-%m-%d")
    a_year_before = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    cursor = conn.cursor()
    query = """CREATE OR REPLACE VIEW top_customers_ticket AS (
                    SELECT customer_email, COUNT(ticket_id) AS num_of_ticket
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent
                    WHERE email = \'%s\' and purchase_date >= \'%s\'
                    GROUP BY customer_email
               )""" % (email, six_month_before)
    cursor.execute(query)

    # cursor.callproc("GetTopCustomerTicket")
    cursor.callproc("GetTopFiveCustomerTicket")
    most_tickets = []
    for result in cursor.stored_results():
        most_tickets = result.fetchall()

    query = """CREATE OR REPLACE VIEW top_customers_commission AS (
                    SELECT customer_email, SUM(price) * 0.1 AS amount_of_commission
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
                    WHERE email = \'%s\' and purchase_date >= \'%s\'
                    GROUP BY customer_email
            )""" % (email, a_year_before)
    cursor.execute(query)

    # cursor.callproc("GetTopCustomerCommission")
    cursor.callproc("GetTopFiveCustomerCommission")
    most_commission = []
    for result in cursor.stored_results():
        most_commission = result.fetchall()

    conn.commit()
    cursor.close()

    for i in range(len(most_tickets)):
        most_tickets[i] = list(most_tickets[i])
    for i in range(len(most_commission)):
        most_commission[i] = list(most_commission[i])
        most_commission[i][-1] = int(most_commission[i][-1])

    return most_tickets, most_commission


def create_new_flight(conn, info):
    cursor = conn.cursor(prepared=True)
    # Check flight num
    query = """SELECT flight_num FROM flight WHERE flight_num = %s"""
    cursor.execute(query, (info["flight_num"],))
    data = cursor.fetchall()
    if data:
        cursor.close()
        return False, "Flight number already exists!"

    # Check departure airport name
    query = """SELECT airport_name FROM airport WHERE airport_name = %s"""
    cursor.execute(query, (info["departure_airport"],))
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Departure airport does not exist in the database!"

    # Check arrival airport name
    query = """SELECT airport_name FROM airport WHERE airport_name = %s"""
    cursor.execute(query, (info["arrival_airport"],))
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Arrival airport does not exist in the database!"

    # Check plane id
    query = """SELECT airplane_id FROM airplane WHERE airplane_id = %s"""
    cursor.execute(query, (info["plane_id"],))
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Airplane does not exist in the database!"

    query = """INSERT INTO flight
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
    print(query % (info["airline_name"], info["flight_num"],
                           info["departure_airport"], info["departure_date"]+" "+info["departure_time"],
                           info["arrival_airport"], info["arrival_date"]+" "+info["arrival_time"],
                           info["price"], info["status"], info["plane_id"]))
    cursor.execute(query, (info["airline_name"], info["flight_num"],
                           info["departure_airport"], info["departure_date"]+" "+info["departure_time"],
                           info["arrival_airport"], info["arrival_date"]+" "+info["arrival_time"],
                           info["price"], info["status"], info["plane_id"]))
    conn.commit()
    cursor.close()
    return True, ""


def change_flight_status(conn, flight_num, status, airline_name):
    cursor = conn.cursor(prepared=True)
    query = """SELECT flight_num, status FROM flight WHERE flight_num = %s AND airline_name = %s"""
    cursor.execute(query, (flight_num, airline_name))
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Flight %s does not exist!" % flight_num
    elif data[0][1] == status:
        cursor.close()
        return False, "Flight %s has the status \'%s\'. Don't need to change" % (flight_num, status)

    query = """UPDATE flight
               SET status = %s
               WHERE flight_num = %s AND airline_name = %s"""
    # print(query)
    cursor.execute(query, (status, flight_num, airline_name))
    conn.commit()
    cursor.close()
    return True, ""


def add_airplane(conn, airline_name, airplane_id, seats):
    cursor = conn.cursor(prepared=True)
    query = """SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s"""
    cursor.execute(query, (airline_name, airplane_id))
    data = cursor.fetchall()
    if data:
        cursor.close()
        return False, "You can not add an existing airplane!"
    query = """INSERT INTO airplane
               VALUES (%s, %s, %s)"""
    cursor.execute(query, (airline_name, airplane_id, seats))
    conn.commit()
    cursor.close()
    return True, ""


def add_airport(conn, airport_name, airport_city):
    cursor = conn.cursor(prepared=True)
    query = """SELECT * FROM airport WHERE airport_name = %s"""
    cursor.execute(query, (airport_name,))
    data = cursor.fetchall()
    if data:
        cursor.close()
        return False, "This airport name already exists!"
    query = """INSERT INTO airport
               VALUES (%s, %s)"""
    cursor.execute(query, (airport_name, airport_city))
    conn.commit()
    cursor.close()
    return True, ""


def view_booking_agents(conn, airline_name):
    PAST_MONTH = (datetime.today() - timedelta(days=31)).strftime("%Y-%m-%d")
    PAST_YEAR = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    cursor = conn.cursor()
    view_query1 = """CREATE OR REPLACE VIEW top_agents_ticket AS (
                        SELECT email, COUNT(ticket_id) AS num_of_ticket
                        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight
                        WHERE purchase_date >= \'%s\' AND airline_name = \'%s\'
                        GROUP BY email
                   )"""
    cursor.execute(view_query1 % (PAST_MONTH, airline_name))
    # cursor.callproc("GetTopAgentsTicket")
    cursor.callproc("GetTopFiveAgentsTicket")
    ticket_month = []
    for result in cursor.stored_results():
        ticket_month = result.fetchall()

    cursor.execute(view_query1 % (PAST_YEAR, airline_name))
    # cursor.callproc("GetTopAgentsTicket")
    cursor.callproc("GetTopFiveAgentsTicket")
    ticket_year = []
    for result in cursor.stored_results():
        ticket_year = result.fetchall()

    view_query2 = """CREATE OR REPLACE VIEW top_agents_commission AS (
                        SELECT email, SUM(price * 0.1) AS amount_of_commission
                        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight
                        WHERE purchase_date >= \'%s\' AND airline_name = \'%s\'
                        GROUP BY email
                   )"""
    cursor.execute(view_query2 % (PAST_YEAR, airline_name))
    cursor.callproc("GetTopAgentsCommission")
    commission_year = []
    for result in cursor.stored_results():
        commission_year = result.fetchall()
    cursor.close()

    for i in range(len(ticket_month)):
        ticket_month[i] = list(ticket_month[i])
        ticket_month[i][1] = int(ticket_month[i][1])
    for i in range(len(ticket_year)):
        ticket_year[i] = list(ticket_month[i])
        ticket_year[i][1] = int(ticket_year[i][1])
    for i in range(len(commission_year)):
        commission_year[i] = list(commission_year[i])
        if commission_year[i][1]:
            commission_year[i][1] = float(commission_year[i][1])
        else:
            commission_year[i][1] = 0

    return ticket_month, ticket_year, commission_year


def view_most_frequent_customer(conn, start_date, end_date, airline_name):
    cursor = conn.cursor(prepared=True)
    query = """SELECT customer_email, COUNT(ticket_id)
               FROM purchases NATURAL JOIN ticket
               WHERE purchase_date BETWEEN %s AND %s AND airline_name = %s
               GROUP BY customer_email
               HAVING COUNT(ticket_id) >= ALL (SELECT COUNT(ticket_id)
                                               FROM purchases NATURAL JOIN ticket
                                               WHERE purchase_date BETWEEN %s AND %s AND airline_name = %s
                                               GROUP BY customer_email)
               ORDER BY customer_email
            """
    # print(query % (start_date, end_date, airline_name, start_date, end_date, airline_name))
    cursor.execute(query, (start_date, end_date, airline_name, start_date, end_date, airline_name))
    most_customer = cursor.fetchall()

    query = """SELECT COUNT(ticket_id)
               FROM purchases NATURAL JOIN ticket
               WHERE purchase_date BETWEEN %s AND %s AND airline_name = %s"""
    # print(query % (start_date, end_date, airline_name))
    cursor.execute(query, (start_date, end_date, airline_name))
    others = cursor.fetchall()
    cursor.close()

    for i in range(len(most_customer)):
        most_customer[i] = list(most_customer[i])
    others[0] = list(others[0])
    if not most_customer:
        most_customer = [["", 0]]
    return most_customer, others


def get_customer_flight(conn, customer_email, airline_name):
    cursor = conn.cursor(prepared=True)
    query = """SELECT DISTINCT flight_num, departure_airport, departure_time, arrival_airport, arrival_time, status, airplane_id
               FROM purchases NATURAL JOIN ticket NATURAL JOIN flight
               WHERE customer_email = %s AND airline_name = %s"""
    print(query)
    cursor.execute(query, (customer_email, airline_name))
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][2] = data[i][2].strftime("%Y-%m-%d")
        data[i][4] = data[i][4].strftime("%Y-%m-%d")
    return data


def get_flight_customers(conn, airline_name, flight_num):
    cursor = conn.cursor(prepared=True)
    # ["Customer email", "Customer name", "Phone number", "passport number", "date of birth"];
    query = """SELECT DISTINCT email, name, phone_number, passport_number, date_of_birth
               FROM ticket NATURAL JOIN purchases JOIN customer ON (customer.email = purchases.customer_email)
               WHERE airline_name = %s AND flight_num = %s"""
    # print(query % (airline_name, flight_num))
    cursor.execute(query, (airline_name, flight_num))
    data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][-1] = data[i][-1].strftime("%Y-%m-%d")
    print(data)
    return data


def view_reports(conn, airline_name, start_date, end_date):
    cursor = conn.cursor(prepared=True)
    query = """SELECT ticket_id, purchase_date
               FROM purchases NATURAL JOIN ticket
               WHERE airline_name = %s AND purchase_date BETWEEN %s AND %s"""
    cursor.execute(query, (airline_name, start_date, end_date))
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][1] = data[i][1].strftime("%Y-%m-%d")
    return data


def get_airline_sales(conn, start_date, end_date, airline_name, t):
    cursor = conn.cursor(prepared=True)
    query = """SELECT SUM(price)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN flight
               WHERE airline_name = %s AND purchase_date BETWEEN %s AND %s
            """
    if t == "direct":
        query += """ AND booking_agent_id IS NULL"""
    else:
        query += """ AND booking_agent_id IS NOT NULL"""
    cursor.execute(query, (airline_name, start_date, end_date))
    data = cursor.fetchall()
    cursor.close()

    if data[0][0] == None:
        return [[0]]
    data[0] = list(data[0])
    data[0][0] = int(data[0][0])
    # print(data)
    return data


def get_top_destinations(conn, start_date, end_date, airline_name):
    cursor = conn.cursor()
    query = """CREATE OR REPLACE VIEW top_destinations AS (
                    SELECT DST.airport_city AS dst, COUNT(ticket_id) AS num_of_purchase
                    FROM flight AS F JOIN airport AS DST ON (F.arrival_airport = DST.airport_name) 
                        NATURAL JOIN purchases NATURAL JOIN ticket
                    WHERE airline_name = \'%s\' AND purchase_date BETWEEN \'%s\' AND \'%s\'
                    GROUP BY dst 
            ) 
            """
    print(query % (airline_name, start_date, end_date))
    cursor.execute(query % (airline_name, start_date, end_date))

    # cursor.callproc("GetTopDestination")
    cursor.callproc("GetTopThreeDestination")
    data = []
    for result in cursor.stored_results():
        data = result.fetchall()

    conn.commit()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])
    return data


def get_user_info(conn, identity, email):
    cursor = conn.cursor()
    query = """SELECT * FROM %s""" % identity
    if identity == "airline_staff":
        query += """ WHERE username = %s"""
    else:
        query += """ WHERE email = %s"""
    cursor.execute(query, (email,))
    data = list(cursor.fetchall()[0])
    if identity == "customer":
        data.pop(2)
    else:
        data.pop(1)
    cursor.close()
    return data


def update_user_info(conn, identity, info, old_email, old_agent_id=""):
    cursor = conn.cursor(prepared=True)
    if info["email"] != old_email:
        query = """SELECT * FROM %s""" % identity
        if identity == "airline_staff":
            query += """ WHERE username = %s"""
        else:
            query += """ WHERE email = %s"""
        cursor.execute(query, (info["email"],))
        data = cursor.fetchall()
        if data:
            cursor.close()
            return False, "Email has already been used!"

    if old_agent_id:
        if info["booking_agent_id"] != old_agent_id:
            query = """SELECT * FROM %s""" % identity
            query += """ WHERE booking_agent_id = %s"""
            cursor.execute(query, (info["booking_agent_id"],))
            data = cursor.fetchall()
            if data:
                cursor.close()
                return False, "Agent id has already been used!"

    query = """UPDATE %s""" % identity
    if identity == "airline_staff":
        query += """ SET username = %s, first_name = %s, last_name = %s
                     WHERE username = %s
                 """
        cursor.execute(query, (info["email"], info["first_name"], info["last_name"], old_email))
    elif identity == "booking_agent":
        query += """ SET email = %s, booking_agent_id = %s
                     WHERE email = %s
                 """
        cursor.execute(query, (info["email"], info["booking_agent_id"], old_email))
    else:
        query += """ SET email = %s, name = %s, building_number = %s, street = %s, city = %s, state = %s, phone_number = %s, passport_number = %s, passport_expiration = %s, passport_country = %s
                     WHERE email = %s
                """
        cursor.execute(query, (info["email"], info["name"], info["building_number"], info["street"], info["city"], info["state"],
                               info["phone_number"], info["passport_number"], info["passport_expiration"], info["passport_country"], old_email))

    conn.commit()
    cursor.close()
    return True, ""
