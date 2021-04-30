from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


PASSWORD_HASH = "md5"


def get_airport_and_city(conn):
    data1 = []
    data2 = []
    cursor = conn.cursor()
    # query = "SELECT airport_city, airport_name FROM `airport`"
    # cursor.execute(query)
    # data1 = cursor.fetchall()
    cursor.callproc("GetAirportWithCity")
    for result in cursor.stored_results():
        data1 = result.fetchall()
    # query = "SELECT DISTINCT airport_city FROM `airport`"
    # cursor.execute(query)
    # data2 = cursor.fetchall()
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
    print(data2)
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
    query = """SELECT password FROM {} WHERE """
    if identity == "airline_staff":
        query += """username = \'{}\'"""
    else:
        query += """email = \'{}\'"""
    cursor.execute(query.format(identity, username.replace("\'", "\'\'")))
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return False
    return check_password_hash(data[0][0], password)


def register_check(conn, email, identity):
    cursor = conn.cursor()
    query = """SELECT """
    if identity == "airline_staff":
        query += "username FROM {} WHERE username = \'{}\'"
    else:
        query += "email FROM {} WHERE email = \'{}\'"
    cursor.execute(query.format(identity, email.replace("\'", "\'\'")))
    data = cursor.fetchall()
    cursor.close()
    return data == []


def register_to_database(conn, info, identity):
    cursor = conn.cursor()
    if identity == "customer":
        query = """INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\') """
        cursor.execute(query.format(identity, info["email"].replace("\'", "\'\'"), info["name"].replace("\'", "\'\'"), generate_password_hash(info["password"], PASSWORD_HASH), info["building_number"],
                                    info["street"].replace("\'", "\'\'"), info["city"].replace("\'", "\'\'"), info["state"], info["phone_number"], info["passport_number"],
                                    info["passport_expiration"], info["passport_country"], info["date_of_birth"]))
    elif identity == "booking_agent":
        query = "INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\')"
        print()
        print(query.format(identity, info["email"], generate_password_hash(info["password"], PASSWORD_HASH), info["booking_agent_id"]))
        print()
        cursor.execute(query.format(identity, info["email"].replace("\'", "\'\'"), generate_password_hash(info["password"], PASSWORD_HASH), info["booking_agent_id"]))
    else:
        query = """INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"""
        print()
        print(query.format(info["email"], generate_password_hash(info["password"], PASSWORD_HASH), info["first_name"], info["last_name"],
                                    info["date_of_birth"], info["airline_name"]))
        print()
        cursor.execute(query.format(info["email"].replace("\'", "\'\'"), generate_password_hash(info["password"], PASSWORD_HASH), info["first_name"].replace("\'", "\'\'"), info["last_name"].replace("\'", "\'\'"),
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
    cursor = conn.cursor()
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
    query = """INSERT INTO ticket
               VALUES (\'%s\', \'%s\', \'%s\')""" % (ticket_id, airline_name, flight_num)
    cursor.execute(query)
    # conn.commit()

    if identity == "customer":
        query = """INSERT INTO purchases
                   VALUES (\'%s\', \'%s\', NULL, \'%s\')""" % (ticket_id, customer_email, today)
    else:
        query = """SELECT booking_agent_id
                   FROM booking_agent
                   WHERE email = \'%s\'""" % agent_email
        cursor.execute(query)
        agent_id = cursor.fetchall()[0][0]
        query = """INSERT INTO purchases
                   VALUES (\'%s\', \'%s\', \'%s\', \'%s\')""" % (ticket_id, customer_email, agent_id, today)
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return True


def get_my_spendings(conn, email):
    cursor = conn.cursor()
    query = """SELECT purchase_date, price
               FROM ticket NATURAL JOIN purchases NATURAL JOIN flight
               WHERE customer_email = \'%s\'
               ORDER BY purchase_date DESC""" % email
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])

    return data


def get_my_commission(conn, email, start_date="", end_date=""):
    cursor = conn.cursor()
    query = """SELECT purchase_data, price * 0.1
               FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
               WHERE email = \'%s\' """ % email
    if start_date:
        query += " AND purchase_date >= \'%s\'" % start_date
    if end_date:
        query += " AND purchase_date <= \'%s\'" % end_date
    query += " ORDER BY purchase_date DESC"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    for i in range(len(data)):
        data[i] = list(data[i])

    return data


def top_customers(conn, email):
    cursor = conn.cursor()
    query = """CREATE OR REPLACE VIEW top_customers AS (
                    SELECT customer_email, COUNT(ticket_id) AS num_of_ticket, SUM(price * 0.1) AS amount_of_commission, purchase_date
                    FROM ticket NATURAL JOIN purchases NATURAL JOIN booking_agent NATURAL JOIN flight
                    WHERE email = \'%s\'
                    GROUP BY customer_email
               )""" % email
    cursor.execute(query)

    six_month_before = (datetime.today() - timedelta(days=6*31)).strftime("%Y-%m-%d")
    query = """SELECT customer_email, num_of_ticket
               FROM top_customers
               WHERE purchase_date >= \'%s\' AND 4 >= (
                    SELECT COUNT(DISTINCT num_of_ticket)
                    FROM top_customers AS t2
                    WHERE t2.num_of_ticket >= num_of_ticket
               )
               ORDER BY num_of_ticekt DESC
            """ % six_month_before
    cursor.execute(query)
    most_tickets = cursor.fetchall()

    a_year_before = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    query = """SELECT customer_email, amount_of_commission
               FROM top_customers
               WHERE purchase_date >= \'%s\' AND 4 >= (
                    SELECT COUNT(DISTINCT amount_of_commission)
                    FROM top_customers AS t2
                    WHERE t2.amount_of_commission >= amount_of_commission
               )
             """ % a_year_before
    cursor.execute(query)
    most_commission = cursor.fetchall()
    cursor.close()

    for i in range(len(most_tickets)):
        most_tickets[i] = list(most_tickets[i])
    for i in range(len(most_commission)):
        most_commission[i] = list(most_commission[i])

    return most_tickets, most_commission
