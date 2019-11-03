import sqlite3

connection = sqlite3.connect("./mini_project.db")
connection.row_factory = sqlite3.Row
c = connection.cursor()

c.execute("PRAGMA foreign_keys=ON;")
connection.commit()