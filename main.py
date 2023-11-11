from PasswordManager import PasswordManagerServer


def connect_to_database_online(driver, server, database, user_id, password):
    db_connection_string = f"Driver={driver};" \
                           f"Server={server};" \
                           f"Database={database};" \
                           f"UID={user_id};"\
                           f"PWD={password};"

    return db_connection_string


def connect_to_database_local(driver, server, database, trusted_connection):
    db_connection_string = f'Driver={driver};' \
                           f'Server={server};' \
                           f'Database={database};' \
                           f'Trusted_Connection={trusted_connection};'

    return db_connection_string


def main():
    db_connection_string = connect_to_database_local("{SQL Server}",
                                                     r"DESKTOP-GFMVUDQ\SQLEXPRESS",
                                                     "PasswordManagerDB",
                                                     "yes")

    password_manager_server = PasswordManagerServer("0.0.0.0", 8080, db_connection_string)

    password_manager_server.start_server()


if __name__ == '__main__':
    main()
