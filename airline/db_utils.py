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


def insert_into_airport(conn, airport, city):
    cursor = conn.cursor()
    query = "INSERT INTO airport VALUES (\'{}\', \'{}\')"
    cursor.execute(query.format(airport, city))
    conn.commit()
    cursor.close()
    return


def get_flights_by_location(conn, source, destination, date):
    pass