import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO lsr_data (name, temp,input_curve,lsr_params) VALUES (?,?, ?, ?)",
            ('Random2', '24','some curve2.IRR', " 2, 34, 43,43,43, 3,4,4 3, 43")
            )

cur.execute("INSERT INTO lsr_data (name, temp,input_curve,lsr_params)  VALUES (?,?, ? ,?)",
            ('Random', '17','some curve.IRR', " 2084, 34, 43,4 3,43, 3,4,4 3, 43")
            )

connection.commit()
connection.close()