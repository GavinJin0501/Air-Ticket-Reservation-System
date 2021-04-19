from werkzeug.security import generate_password_hash, check_password_hash

PASSWORD_HASH = "md5"


def register_check(conn, username):
    cursor = conn.cursor()
    query = "SELECT * FROM user WHERE username = \'{}\'"
    cursor.execute(query.format(username))
    data = cursor.fetchone()
    cursor.close()
    return data


def register_store(conn, username, password):
    cursor = conn.cursor()
    query = "INSERT INTO user VALUES(\'{}\', \'{}\')"
    cursor.execute(query.format(username, generate_password_hash(password, PASSWORD_HASH)))
    conn.commit()
    cursor.close()
    return


def login_check(conn, username, password):
    cursor = conn.cursor()
    query = "SELECT * FROM user WHERE username = \'{}\'"
    cursor.execute(query.format(username))
    data = cursor.fetchall()
    status = check_password_hash(data[0][1], password)
    cursor.close()
    return status

