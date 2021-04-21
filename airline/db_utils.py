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
    print("==============")
    cursor = conn.cursor()
    query = """SELECT * 
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
    for each in data:
        print(each)
    cursor.close()
    return []
