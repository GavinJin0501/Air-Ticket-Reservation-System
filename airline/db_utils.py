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


def get_flights_by_location(conn, date, src_city, dst_city, src_airport="", dst_airport=""):
    cursor = conn.cursor()
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id 
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name)
               WHERE F.departure_time LIKE \'{}%\' AND F.status = 'Upcoming' AND """
    # city+airport -> city+airport
    if src_airport and dst_airport:
        query += """F.departure_airport = \'{}\' AND F.arrival_airport = \'{}\' ORDER BY F.departure_time"""
        cursor.execute(query.format(date, src_airport, dst_airport))
    # city+airport -> city
    elif src_airport:
        query += """F.departure_airport = \'{}\' AND DST.airport_city= \'{}\' ORDER BY F.departure_time"""
        cursor.execute(query.format(date, src_airport, dst_city))
    # city -> city+airport
    elif dst_airport:
        query += """SRC.airport_city = \'{}\' AND F.arrival_airport = \'{}\' ORDER BY F.departure_time"""
        cursor.execute(query.format(date, src_city, dst_airport))
    # city -> city
    else:
        query += """SRC.airport_city = \'{}\' AND DST.airport_city= \'{}\' ORDER BY F.departure_time"""
        cursor.execute(query.format(date, src_city, dst_city))
    data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][4] = data[i][4].strftime("%Y-%m-%d %H:%M:%S")
        data[i][7] = data[i][7].strftime("%Y-%m-%d %H:%M:%S")
        data[i][8] = int(data[i][8])

    return data


def login_check(conn, username, password, identity):
    cursor = conn.cursor()
    query = """SELECT password FROM %s WHERE """ % identity
    if identity == "airline_staff":
        query += """username = \'%s\'"""
    else:
        query += """email = \'%s\'"""
    cursor.execute(query % username.replace("\'", "\'\'"))
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return False
    return check_password_hash(data[0][0], password)


def airline_staff_initialization(conn, email):
    cursor = conn.cursor()
    query = """SELECT airline_name FROM airline_staff WHERE username = \'%s\'""" % email
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data[0][0]


def register_check(conn, info, identity):
    cursor = conn.cursor()
    if identity == "airline_staff":
        query = """SELECT airline_name FROM airline WHERE airline_name = \'%s\'""" % info["airline_name"]
        print(query)
        cursor.execute(query)
        data = cursor.fetchall()
        if not data:
            cursor.close()
            return False, "No such airline"
        query = "SELECT username FROM %s WHERE username = \'%s\'" % (identity, info["email"].replace("\'", "\'\'"))
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        if data:
            return False, "Email has already been used"
        else:
            return True, ""
    else:
        query = "SELECT email FROM %s WHERE email = \'%s\'" % (identity, info["email"].replace("\'", "\'\'"))
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        if data:
            return False, "Email has already been used"
        else:
            return True, ""


def register_to_database(conn, info, identity):
    cursor = conn.cursor()
    if identity == "customer":
        query = """INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\') """
        cursor.execute(query.format(identity, info["email"].replace("\'", "\'\'"), info["name"].replace("\'", "\'\'"), generate_password_hash(info["password"], PASSWORD_HASH), info["building_number"],
                                    info["street"].replace("\'", "\'\'"), info["city"].replace("\'", "\'\'"), info["state"], info["phone_number"], info["passport_number"],
                                    info["passport_expiration"], info["passport_country"], info["date_of_birth"]))
    elif identity == "booking_agent":
        query = "INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\')"
        cursor.execute(query.format(identity, info["email"].replace("\'", "\'\'"), generate_password_hash(info["password"], PASSWORD_HASH), info["booking_agent_id"]))
    else:
        query = """INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"""
        cursor.execute(query.format(identity, info["email"].replace("\'", "\'\'"), generate_password_hash(info["password"], PASSWORD_HASH), info["first_name"].replace("\'", "\'\'"), info["last_name"].replace("\'", "\'\'"),
                                    info["date_of_birth"], info["airline_name"]))
    conn.commit()
    cursor.close()
    return


def get_flight_status(conn, flight_num, departure_date, arrival_date):
    cursor = conn.cursor()
    query = """SELECT airline_name, flight_num, status, airport_city, departure_time
                FROM flight JOIN airport ON (flight.arrival_airport = airport.airport_name) """
    if not flight_num:
        query += """WHERE departure_time LIKE \'{}%\'"""
        cursor.execute(query.format(departure_date))
        data = cursor.fetchall()
    else:
        query += """WHERE flight_num = \'%s\' AND """ % flight_num
        if departure_date and arrival_date:
            query += """departure_time LIKE \'{}%\' AND arrival_time LIKE \'{}%\'"""
            cursor.execute(query.format(departure_date, arrival_date))
            data = cursor.fetchall()
        elif departure_date:
            query += """departure_time LIKE \'{}%\'"""
            cursor.execute(query.format(departure_date))
            data = cursor.fetchall()
        else:
            query += """arrival_time LIKE \'{}%\'"""
            cursor.execute(query.format(arrival_date))
            data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][-1] = data[i][-1].strftime("%Y-%m-%d %H:%M:%S")

    return data


def get_upcoming_flights(conn, identity, email):
    cursor = conn.cursor()
    email = email.replace("\'", "\'\'")
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name) """
    if identity == "airline_staff":
        query += """WHERE airline_name IN (
                        SELECT airline_name
                        FROM airline_staff
                        WHERE username = \'%s\'
        )"""
    elif identity == "customer":
        query += """WHERE flight_num IN (
                        SELECT flight_num
                        FROM purchases NATURAL JOIN ticket
                        WHERE customer_email = \'%s\'
        )"""
    else:
        query += """WHERE flight_num IN (
                        SELECT flight_num
                        FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent
                        WHERE email =  \'%s\'
        )"""

    # print("get upcoming flights query is:\n", query % email)
    cursor.execute(query % email)
    data = cursor.fetchall()
    cursor.close()

    # need to pre-process the data!!!!
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][4] = data[i][4].strftime("%Y-%m-%d %H:%M:%S")
        data[i][7] = data[i][7].strftime("%Y-%m-%d %H:%M:%S")
        data[i][8] = int(data[i][8])
    return data


def purchase_ticket(conn, identity, customer_email, agent_email, airline_name, flight_num):
    cursor = conn.cursor(prepared=True)
    query = """SELECT COUNT(ticket_id) 
               FROM ticket 
               WHERE flight_num = \'%s\'""" % flight_num
    # print(query)
    cursor.execute(query)
    ticket_num = cursor.fetchall()
    ticket_num = ticket_num[0][0] if ticket_num else 0
    query = """SELECT seats 
               FROM airplane NATURAL JOIN flight 
               WHERE flight_num = \'%s\'""" % flight_num
    # print(query)
    cursor.execute(query)
    seat_num = cursor.fetchall()
    seat_num = seat_num[0][0] if seat_num else 0
    # print(ticket_num, seat_num)
    if ticket_num >= seat_num:
        return False

    ticket_id = flight_num[:2] + datetime.now().strftime("%Y%m%d%H%M%S")
    today = datetime.today().strftime("%Y-%m-%d")
    t = (ticket_id, airline_name, flight_num)
    query = """INSERT INTO ticket
               VALUES (%s, %s, %s)"""
    cursor.execute(query, t)
    # conn.commit()

    if identity == "customer":
        query = """INSERT INTO purchases
                   VALUES (%s, %s, NULL, %s)"""
        t = (ticket_id, customer_email, today)
    else:
        query = """SELECT booking_agent_id
                   FROM booking_agent
                   WHERE email = \'%s\'""" % agent_email
        cursor.execute(query)
        agent_id = cursor.fetchall()[0][0]
        query = """INSERT INTO purchases
                   VALUES (%s, %s, %s, %s)"""
        t = (ticket_id, customer_email, agent_id, today)
    cursor.execute(query, t)
    conn.commit()
    cursor.close()
    return True


def get_my_spendings_total_amount(conn, email, start_date, end_date):
    cursor = conn.cursor()
    query = """SELECT SUM(price)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN flight
               WHERE customer_email = \'%s\' AND purchase_date BETWEEN \'%s\' AND \'%s\'
            """ % (email, start_date, end_date)
    # print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    if data[0][0] == None:
        return 0
    else:
        return data[0][0]


def get_my_spendings_certain_range(conn, email, start_date, end_date):
    cursor = conn.cursor()
    query = """SELECT purchase_date, price
                FROM ticket NATURAL JOIN purchases NATURAL JOIN flight
                WHERE customer_email = \'%s\' AND purchase_date BETWEEN \'%s\' AND \'%s\'
            """ % (email, start_date, end_date)
    # print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][0] = data[i][0].strftime("%Y-%m-%d")
        data[i][1] = int(data[i][1])
    return data


def get_my_commission(conn, email, start_date, end_date):
    cursor = conn.cursor()
    query = """SELECT SUM(price) * 0.1, COUNT(ticket_id), SUM(price) * 0.1 / COUNT(ticket_id)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
               WHERE email = \'%s\' AND purchase_date BETWEEN \'%s\' AND \'%s\'
            """ % (email, start_date, end_date)
    cursor.execute(query)
    my_commission = cursor.fetchall()

    query = """SELECT SUM(price) * 0.1, COUNT(ticket_id), SUM(price) * 0.1 / COUNT(ticket_id)
               FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
               WHERE purchase_date BETWEEN \'%s\' AND \'%s\'
            """ % (start_date, end_date)
    print(query)
    cursor.execute(query)
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
    six_month_before = (datetime.today() - timedelta(days=6*31)).strftime("%Y-%m-%d")
    a_year_before = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    cursor = conn.cursor()
    query = """CREATE OR REPLACE VIEW top_customers_ticket AS (
                    SELECT customer_email, COUNT(ticket_id) AS num_of_ticket
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent
                    WHERE email = \'%s\' and purchase_date >= \'%s\'
                    GROUP BY customer_email
               )""" % (email, six_month_before)
    cursor.execute(query)

    query = """SELECT *
               FROM top_customers_ticket AS t1
               WHERE 4 >= (
                    SELECT COUNT(DISTINCT t2.num_of_ticket)
                    FROM top_customers_ticket AS t2
                    WHERE t2.num_of_ticket > t1.num_of_ticket
               )
               ORDER BY t1.num_of_ticket DESC
            """
    cursor.execute(query)
    most_tickets = cursor.fetchall()

    query = """CREATE OR REPLACE VIEW top_customers_commission AS (
                    SELECT customer_email, SUM(price) AS amount_of_commission
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
                    WHERE email = \'%s\' and purchase_date >= \'%s\'
                    GROUP BY customer_email
            )""" % (email, six_month_before)
    cursor.execute(query)

    query = """SELECT *
               FROM top_customers_commission AS t1
               WHERE 4 >= (
                    SELECT COUNT(DISTINCT t2.amount_of_commission)
                    FROM top_customers_commission AS t2
                    WHERE t1.amount_of_commission > t1.amount_of_commission
               )
             """
    cursor.execute(query)
    most_commission = cursor.fetchall()

    conn.commit()
    cursor.close()

    for i in range(len(most_tickets)):
        most_tickets[i] = list(most_tickets[i])
    for i in range(len(most_commission)):
        most_commission[i] = list(most_commission[i])
        most_commission[i][-1] = int(most_commission[i][-1])

    return most_tickets, most_commission


def create_new_flight(conn, info):
    cursor = conn.cursor()
    # Check flight num
    query = """SELECT flight_num FROM flight WHERE flight_num = \'%s\'""" % info["flight_num"]
    cursor.execute(query)
    data = cursor.fetchall()
    if data:
        cursor.close()
        return False, "Flight number already exists!"

    # Check departure airport name
    query = """SELECT departure_airport FROM flight WHERE departure_airport = \'%s\'""" % info["departure_airport"]
    cursor.execute(query)
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Departure airport does not exist in the database!"

    # Check arrival airport name
    query = """SELECT arrival_airport FROM flight WHERE arrival_airport = \'%s\'""" % info["arrival_airport"]
    cursor.execute(query)
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Arrival airport does not exist in the database!"

    # Check plane id
    query = """SELECT airplane_id FROM airplane WHERE airplane_id = \'%s\'""" % info["plane_id"]
    cursor.execute(query)
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Airplane does not exist in the database!"

    query = """INSERT INTO flight
               VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d, \'%s\', \'%s\')
            """ % (info["airline_name"], info["flight_num"], info["departure_airport"], info["departure_time"], info["arrival_airport"], info["arrival_time"], int(info["price"]), info["status"], info["plane_id"])
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return True, ""


def change_flight_status(conn, flight_num, status):
    cursor = conn.cursor()
    query = """SELECT flight_num, status FROM flight WHERE flight_num = \'%s\'""" % flight_num
    cursor.execute(query)
    data = cursor.fetchall()
    if not data:
        cursor.close()
        return False, "Flight %s does not exist!" % flight_num
    elif data[0][1] == status:
        cursor.close()
        return False, "Flight %s has the status \'%s\'. Don't need to change" % (flight_num, status)

    query = """UPDATE flight
               SET status = \'%s\'
               WHERE flight_num = \'%s\'""" % (status, flight_num)
    print(query)
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return True, ""


def add_airplane(conn, airline_name, airplane_id, seats):
    cursor = conn.cursor()
    query = """SELECT * FROM airplane WHERE airline_name = \'%s\' AND airplane_id = \'%s\'""" % (airline_name, airplane_id)
    cursor.execute(query)
    data = cursor.fetchall()
    if data:
        cursor.close()
        return False, "You can not add an existing airplane!"
    query = """INSERT INTO airplane
               VALUES (\'%s\', \'%s\', \'%s\')""" % (airline_name, airplane_id, seats)
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return True, ""


def add_airport(conn, airport_name, airport_city):
    cursor = conn.cursor()
    query = """SELECT * FROM airport WHERE airport_name = \'%s\'""" % airport_name
    cursor.execute(query)
    data = cursor.fetchall()
    if data:
        cursor.close()
        return False, "This airport name already exists!"
    query = """INSERT INTO airport
               VALUES ('%s\', \'%s\')""" % (airport_name, airport_city)
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return True, ""


def view_booking_agents(conn):
    PAST_MONTH = (datetime.today() - timedelta(days=31)).strftime("%Y-%m-%d")
    PAST_YEAR = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    cursor = conn.cursor()
    view_query1 = """CREATE OR REPLACE VIEW top_agents_ticket AS (
                        SELECT email, COUNT(ticket_id) AS num_of_ticket
                        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight
                        WHERE purchase_date >= \'%s\'
                        GROUP BY email
                   )"""
    cursor.execute(view_query1 % PAST_MONTH)
    query = """SELECT *
               FROM top_agents_ticket AS t1
               WHERE 4 >= (
                    SELECT COUNT(DISTINCT t2.num_of_ticket)
                    FROM top_agents_ticket AS t2
                    WHERE t2.num_of_ticket > t1.num_of_ticket
               )"""
    cursor.execute(query)
    ticket_month = cursor.fetchall()

    cursor.execute(view_query1 % PAST_YEAR)
    cursor.execute(query)
    ticket_year = cursor.fetchall()

    view_query2 = """CREATE OR REPLACE VIEW top_agents_commission AS (
                        SELECT email, SUM(price * 0.1) AS amount_of_commission
                        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight
                        WHERE purchase_date >= \'%s\'
                        GROUP BY email
                   )"""
    cursor.execute(view_query2 % PAST_YEAR)
    query = """SELECT *
               FROM top_agents_commission AS t1
               WHERE 4 >= (
                    SELECT COUNT(DISTINCT t2.amount_of_commission)
                    FROM top_agents_commission AS t2
                    WHERE t2.amount_of_commission > t1.amount_of_commission
               )"""
    cursor.execute(query)
    commission_year = cursor.fetchall()
    cursor.close()
    return ticket_month, ticket_year, commission_year