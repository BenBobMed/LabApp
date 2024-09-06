from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#import globals  # Import the globals module
import win32com.client as win32
from tkinter import messagebox


def create_tables():
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    # Create Reservations table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id TEXT NOT NULL,
        check_in DATE NOT NULL,
        check_out DATE NOT NULL,
        user_id INTEGER NOT NULL
    )
    ''')

    # Create users table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def check_availability(selected_equipment, check_in_date):
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    # Check reservations for the equipment and selected date
    cursor.execute('''
        SELECT * FROM Reservations 
        WHERE equipment_id = ? AND ? BETWEEN check_in AND check_out
    ''', (selected_equipment, check_in_date))
    
    reservation = cursor.fetchone()
    conn.close()

    return not bool(reservation)  # Return True if available, False otherwise

def update_availability(*args):
    selected_equipment = equipments.get(equipment_var.get(), None)
    check_in_date = check_in_cal.get_date()

    if selected_equipment and check_in_date:
        available = check_availability(selected_equipment, check_in_date)
        
        if available:
            availability_label.config(text="Disponible", fg="green")
        else:
            availability_label.config(text="Non disponible", fg="red")
    else:
        availability_label.config(text="Sélectionnez un équipement et une date", fg="black")

def book_equipment():
    selected_equipment = equipments.get(equipment_var.get(), None)
    check_in_date = check_in_cal.get_date()
    check_out_date = check_out_cal.get_date()

    # Validate inputs
    if not selected_equipment:
        messagebox.showerror('Erreur', 'Veuillez sélectionner un équipement.')
        return

    if check_in_date is None or check_out_date is None:
        messagebox.showerror('Erreur', 'Veuillez sélectionner les dates de check-in et de check-out.')
        return

    if check_in_date > check_out_date:
        messagebox.showerror('Erreur', 'La date de check-out doit être après la date de check-in.')
        return

    # Check if the user is logged in
    if globals.authenticated_id is None or globals.authenticated_email is None:
        messagebox.showerror('Erreur', 'Veuillez vous connecter pour réserver un équipement.')
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    # Check for conflicting reservations
    cursor.execute('''
        SELECT * FROM Reservations 
        WHERE equipment_id = ? AND (
            (check_in < ? AND check_out > ?) OR
            (check_in < ? AND check_out > ?)
        )
    ''', (selected_equipment, check_out_date, check_in_date, check_in_date, check_out_date))

    if cursor.fetchone():
        conn.close()
        messagebox.showerror('Erreur', 'Cet équipement est déjà réservé pour ces dates.')
        return

    # Insert the new reservation into the database
    cursor.execute('''
        INSERT INTO Reservations (equipment_id, check_in, check_out, user_id)
        VALUES (?, ?, ?, ?)
    ''', (selected_equipment, check_in_date, check_out_date, globals.authenticated_id))
    conn.commit()
    conn.close()

    # Send a confirmation email to the user
    subject = "Confirmation de réservation d'équipement"
    body = f"Bonjour,\n\nVotre réservation pour l'équipement {selected_equipment} a été confirmée.\n\nDétails de la réservation:\nDate de début: {check_in_date}\nDate de fin: {check_out_date}\n\nMerci!"
    send_email(globals.authenticated_email, subject, body)

    messagebox.showinfo('Succès', 'Réservation réussie! Un email de confirmation a été envoyé à votre adresse.')

def cancel_reservation():
    selected_equipment = equipments.get(equipment_var.get(), None)

    if not selected_equipment:
        messagebox.showerror('Erreur', 'Veuillez sélectionner un équipement à annuler.')
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Reservations 
        WHERE user_id = ? AND equipment_id = ?
    ''', (globals.authenticated_id, selected_equipment))
    
    if cursor.rowcount == 0:
        messagebox.showerror('Erreur', 'Aucune réservation trouvée pour cet utilisateur et cet équipement.')
        conn.close()
        return
    
    conn.commit()

    cursor.execute('SELECT email FROM users WHERE id = ?', (globals.authenticated_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        messagebox.showerror('Erreur', 'Aucun utilisateur trouvé pour cet ID.')
    else:
        user_email = result[0]
        subject = "Annulation de réservation d'équipement"
        body = f"Bonjour,\n\nVotre réservation pour l'équipement {selected_equipment} a été annulée.\n\nMerci!"
        send_email(user_email, subject, body)

        messagebox.showinfo('Succès', 'Réservation annulée! Un email de confirmation a été envoyé.')

def send_email(user_email, subject, body):
    try:
        # Create an instance of the Outlook application
        outlook = win32.Dispatch('outlook.application')
        
        # Create a new mail item
        mail = outlook.CreateItem(0)  # 0 represents a new mail item
        
        mail.To = user_email
        mail.Subject = subject
        mail.Body = body
        
        # Send the email
        mail.Send()
        print(f"Email sent successfully to {user_email}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de l'envoi de l'email: {e}")

def view_user_reservations():
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT equipment_id, check_in, check_out 
        FROM Reservations 
        WHERE user_id = ?
    ''', (globals.authenticated_id,))
    
    reservations = cursor.fetchall()
    conn.close()

    for row in tree.get_children():
        tree.delete(row)
    
    if reservations:
        for reservation in reservations:
            tree.insert("", "end", values=reservation)
    else:
        messagebox.showinfo("Information", "Aucune réservation trouvée pour cet utilisateur.")

def get_material_identifiers() -> dict:
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    # Get material identifiers
    cursor.execute('''
        SELECT mat_ref, mat_ref FROM Mat;
    ''')
    
    mat_identifiers = cursor.fetchall()
    conn.close()

    return {f"{mat_ref} ({mat_ref})": mat_ref for (mat_ref, mat_ref) in mat_identifiers}
    
def create_ui():
    global check_in_cal, check_out_cal, equipment_var, equipments, tree, availability_label

    create_tables()

    user_window = Tk()
    user_window.title('Réservation d\'équipement')
    user_window.geometry('1200x800')

    canvas = Canvas(user_window, width=600, height=700)
    canvas.pack(fill='both', expand=True)

    color1 = "#ADD8E6"  # light blue
    color2 = "#FFFFFF"  # white
    r1, g1, b1 = user_window.winfo_rgb(color1)
    r2, g2, b2 = user_window.winfo_rgb(color2)
    r_ratio = (r2 - r1) / 700
    g_ratio = (g2 - g1) / 700
    b_ratio = (b2 - b1) / 700

    for i in range(700):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = f'#{nr:04x}{ng:04x}{nb:04x}'
        canvas.create_line(0, i, 600, i, fill=color, width=2)

    container = Frame(user_window, bg='#ADD8E6')
    container.place(relwidth=1, relheight=1)

    equipment_var = StringVar()

    Label(container, text="Choisissez l'équipement", bg='#ADD8E6', fg='black').pack(pady=10)

    equipments = get_material_identifiers()  # Dictionary of equipment

    equipment_menu = OptionMenu(container, equipment_var, *equipments.keys())
    equipment_menu.pack(pady=10)
    equipment_menu.config(width=20)

    # Display availability
    availability_label = Label(container, text="Sélectionnez un équipement et une date", bg='#ADD8E6', fg='black')
    availability_label.pack(pady=10)

    Label(container, text="Choisissez la date de check-in", bg='#ADD8E6', fg='black').pack(pady=10)
    check_in_cal = Calendar(container, selectmode='day', date_pattern='yyyy-mm-dd')
    check_in_cal.pack(pady=10)

    Label(container, text="Choisissez la date de check-out", bg='#ADD8E6', fg='black').pack(pady=10)
    check_out_cal = Calendar(container, selectmode='day', date_pattern='yyyy-mm-dd')
    check_out_cal.pack(pady=10)

    # Check availability when check-in date or equipment is selected
    check_in_cal.bind("<<CalendarSelected>>", update_availability)
    equipment_var.trace('w', update_availability)

    book_button = Button(container, text="Réserver", command=book_equipment, bg='white', fg='black')
    book_button.pack(pady=20)

    cancel_button = Button(container, text="Annuler une réservation", command=cancel_reservation, bg='white', fg='black')
    cancel_button.pack(pady=20)

    view_button = Button(container, text="Voir les réservations de l'utilisateur", command=view_user_reservations, bg='white', fg='black')
    view_button.pack(pady=20)

    # Reservations table
    columns = ("equipment_id", "check_in", "check_out")
    tree = ttk.Treeview(container, columns=columns, show="headings")
    tree.heading("equipment_id", text="ID de l'équipement")
    tree.heading("check_in", text="Date de check-in")
    tree.heading("check_out", text="Date de check-out")
    tree.pack(pady=20, fill='x')

    user_window.mainloop()

if __name__ == "__main__":
    create_ui()
