import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Connect to the database
conn = sqlite3.connect('userdata.db')
cursor = conn.cursor()

try:
    # Insert random data into 'data' table (which represents 'users')
    email = fake.email()
    password = fake.password()
    username = fake.name()
    cursor.execute('INSERT INTO data (email, utilisateur, password) VALUES (?, ?, ?)',
                   (email, username, password))
    conn.commit()

    # Retrieve the user_id of the inserted user
    user_id = cursor.lastrowid

    # Insert random data into 'Lab' table
    duration = random.randint(1, 5)  # Random duration between 1 and 5
    cursor.execute('INSERT INTO Lab (duration) VALUES (?)',
                   (duration,))
    conn.commit()

    # Retrieve the Lab_ID of the inserted lab
    lab_id = cursor.lastrowid

    # Insert random data into 'Mat' table
    mat_ref = fake.uuid4()  # Generate a unique reference for the material
    mat_categ = fake.word()  # Random material category
    mat_qte = random.randint(1, 100)  # Random quantity between 1 and 100
    cursor.execute('INSERT INTO Mat (mat_ref, mat_categ, mat_Qte) VALUES (?, ?, ?)',
                   (mat_ref, mat_categ, mat_qte))
    conn.commit()

    # Retrieve the mat_ref of the inserted material
    mat_ref_id = mat_ref  # As mat_ref is a primary key, use it directly

    # Generate random start and end times for reservation
    start_time = fake.date_time_this_year()
    end_time = start_time + timedelta(hours=random.randint(1, 4))  # Add 1 to 4 hours

    # Insert random data into 'Resrvation_Lab' table
    cursor.execute('INSERT INTO Resrvation_Lab (Lab_ID, res_Start, res_End, user_id) VALUES (?, ?, ?, ?)',
                   (lab_id, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    conn.commit()

    # Insert random data into 'Resrvation_Mat' table
    cursor.execute('INSERT INTO Resrvation_Mat (mat_ref, res_Start, res_End, user_id) VALUES (?, ?, ?, ?)',
                   (mat_ref_id, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    conn.commit()

finally:
    # Ensure the connection is closed even if an error occurs
    conn.close()
