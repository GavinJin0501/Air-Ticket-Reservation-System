from werkzeug.security import generate_password_hash, check_password_hash

PASSWORD_HASH = "md5"


def get_flights_by_location(conn, source, destination, date):
    cursor = conn.cursor()
    query = "SELECT * FROM "