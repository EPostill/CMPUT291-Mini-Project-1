import sqlite3


path_found = False
while not path_found:
    print('Welcome to Mini Project 1')
    db_path = "./" + input("Please enter name of database: ")
    print(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    c = connection.cursor()
    c.execute("PRAGMA foreign_keys=ON;")
    path_found = True
    try:
        c.execute("""SELECT * FROM users""")
    except:
        print("That database does not exist")
        path_found = False

    connection.commit()
