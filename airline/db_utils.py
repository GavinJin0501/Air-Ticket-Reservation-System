from werkzeug.security import generate_password_hash, check_password_hash

PASSWORD_HASH = "md5"


def get_airport_and_city(conn):
    cursor = conn.cursor()
    query = "SELECT * FROM `airport` ORDER BY airport_city"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        data[i] = data[i][1] + " - " + data[i][0]
    # print(data)
    return data


def get_flights_by_location(conn, source, destination, date):
    cursor = conn.cursor()
    query = "SELECT * FROM "