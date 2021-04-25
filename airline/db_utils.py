from werkzeug.security import generate_password_hash, check_password_hash

PASSWORD_HASH = "md5"


def get_airport_and_city(conn):
    cursor = conn.cursor()
    query = "SELECT airport_city, airport_name FROM `airport`"
    cursor.execute(query)
    data1 = cursor.fetchall()
    query = "SELECT DISTINCT airport_city FROM `airport`"
    cursor.execute(query)
    data2 = cursor.fetchall()
    cursor.close()
    for i in range(len(data1)):
        data1[i] = data1[i][0] + " - " + data1[i][1]
    for i in range(len(data2)):
        data2[i] = data2[i][0]
    data2 += data1
    data2.sort()
    return data2


def get_flights_by_location(conn, date, src_city, dst_city, src_airport="", dst_airport=""):
    cursor = conn.cursor()
    query = """SELECT airline_name, flight_num, departure_airport, SRC.airport_city, departure_time,
                      arrival_airport, DST.airport_city, arrival_time, price, status, airplane_id 
               FROM flight AS F JOIN airport AS SRC ON (F.departure_airport = SRC.airport_name) 
                                JOIN airport AS DST ON (F.arrival_airport = DST.airport_name)
               WHERE F.departure_time LIKE \'{}%\' AND """
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
        data[i] = data[i][:4] + [data[i][4].strftime("%Y/%m/%d %H:%M:%S"), data[i][5], data[i][6],
                                 data[i][7].strftime("%Y/%m/%d %H:%M:%S"), int(data[i][8])] \
                  + data[i][9:]
    # print()
    # for each in data:
    #     print(each)
    # print()
    return data


def login_check(conn, username, password, identity):
    cursor = conn.cursor()
    query = """SELECT password FROM {} WHERE """
    if identity == "airline_staff":
        query += """username = \'{}\'"""
    else:
        query += """email = \'{}\'"""
    cursor.execute(query.format(identity, username))
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
    # print()
    # print(query)
    # print()
    cursor.execute(query.format(identity, email))
    data = cursor.fetchall()
    cursor.close()
    return data == []


def register_to_database(conn, info, identity):
    cursor = conn.cursor()
    if identity == "customer":
        query = """INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\') """
        print()
        print(query.format(identity, info["email"], info["name"], generate_password_hash(info["password"], PASSWORD_HASH), info["building_number"],
                                    info["street"], info["city"], info["state"], info["phone_number"], info["passport_number"],
                                    info["passport_expiration"], info["passport_country"], info["date_of_birth"]))
        print()
        cursor.execute(query.format(identity, info["email"], info["name"], generate_password_hash(info["password"], PASSWORD_HASH), info["building_number"],
                                    info["street"], info["city"], info["state"], info["phone_number"], info["passport_number"],
                                    info["passport_expiration"], info["passport_country"], info["date_of_birth"]))
    elif identity == "booking_agent":
        query = "INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\')"
        print()
        print(query.format(identity, info["email"], generate_password_hash(info["password"], PASSWORD_HASH), info["booking_agent_id"]))
        print()
        cursor.execute(query.format(identity, info["email"], generate_password_hash(info["password"], PASSWORD_HASH), info["booking_agent_id"]))
    else:
        query = """INSERT INTO {} VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"""
        print()
        print(query.format(info["email"], generate_password_hash(info["password"], PASSWORD_HASH), info["first_name"], info["last_name"],
                                    info["date_of_birth"], info["airline_name"]))
        print()
        cursor.execute(query.format(info["email"], generate_password_hash(info["password"], PASSWORD_HASH), info["first_name"], info["last_name"],
                                    info["date_of_birth"], info["airline_name"]))
    conn.commit()
    cursor.close()
    return