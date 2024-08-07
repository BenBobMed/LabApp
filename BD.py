import sqlite3

#Test

# Connect to the database (or create it if it doesn't exist)

conn = sqlite3.connect('userdata.db')

cursor = conn.cursor()



# Create the 'users' table

cursor.execute('''

    CREATE TABLE IF NOT EXISTS data (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT NOT NULL UNIQUE,

        utilisateur TEXT NOT NULL,

        password TEXT NOT NULL,

        is_admin INTEGER DEFAULT 0

    )

''')



# Commit the changes and close the connection

conn.commit()





# Create the 'Lat' table with 'mat_ref' as the primary key

cursor.execute('''

    CREATE TABLE IF NOT EXISTS Lab (

        Lab_ID INTEGER PRIMARY KEY AUTOINCREMENT,

        duration INTEGER NOT NULL

    )

''')



# Commit the changes and close the connection

conn.commit()



# Commit the changes and close the connection

conn.commit()





# Create the 'Resrvation_Lab' table

cursor.execute('''

    CREATE TABLE IF NOT EXISTS Resrvation_Lab (

        res_lab_id INTEGER PRIMARY KEY AUTOINCREMENT,

        Lab_ID INTEGER NOT NULL,

        res_Start TEXT NOT NULL,

        res_End TEXT NOT NULL,

        user_id INTEGER NOT NULL,

        FOREIGN KEY (Lab_ID) REFERENCES Lab (Lab_ID),

        FOREIGN KEY (user_id) REFERENCES users (user_id)

    )

''')



import sqlite3



# Connect to the database

conn = sqlite3.connect('userdata.db')

cursor = conn.cursor()



# Create the 'Mat' table with the correct column names

cursor.execute('''

    CREATE TABLE IF NOT EXISTS Mat (

        mat_ref TEXT PRIMARY KEY,

        mat_categ TEXT NOT NULL,

        mat_Qte INTEGER NOT NULL

    )

''')



# Create the 'Resrvation_Mat' table with the correct column names

cursor.execute('''

    CREATE TABLE IF NOT EXISTS Resrvation_Mat (

        res_mat_id INTEGER PRIMARY KEY AUTOINCREMENT,

        mat_ref TEXT NOT NULL,

        res_Start TEXT NOT NULL,

        res_End TEXT NOT NULL,

        user_id INTEGER NOT NULL,

        FOREIGN KEY (mat_ref) REFERENCES Mat (mat_ref),

        FOREIGN KEY (user_id) REFERENCES data (id)

    )

''')



# Commit the changes and close the connection

conn.commit()

conn.close()

