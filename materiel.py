from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
import win32com.client as win32

# Fonction pour envoyer un email via Outlook
def send_email_via_outlook(to, subject, body):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = subject
    mail.Body = body
    mail.Send()

def create_tables():
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    # Créer la table Reservations si elle n'existe pas déjà
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id TEXT NOT NULL,
        check_in DATE NOT NULL,
        check_out DATE NOT NULL,
        user_id INTEGER NOT NULL
    )
    ''')

    # Créer la table users si elle n'existe pas déjà
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

    # Vérifier les réservations pour l'équipement et la date sélectionnée
    cursor.execute('''
        SELECT * FROM Reservations 
        WHERE equipment_id = ? AND ? BETWEEN check_in AND check_out
    ''', (selected_equipment, check_in_date))
    
    reservation = cursor.fetchone()
    conn.close()

    if reservation:
        return False  # Non disponible
    else:
        return True  # Disponible

def update_availability(*args):
    selected_equipment = equipment_var.get()
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
    selected_equipment = equipment_var.get()
    check_in_date = check_in_cal.get_date()
    check_out_date = check_out_cal.get_date()

    # Vérifications des entrées
    if not selected_equipment:
        messagebox.showerror('Erreur', 'Veuillez sélectionner un équipement.')
        return

    if check_in_date is None or check_out_date is None:
        messagebox.showerror('Erreur', 'Veuillez sélectionner les dates de check-in et de check-out.')
        return

    if check_in_date > check_out_date:
        messagebox.showerror('Erreur', 'La date de check-out doit être après la date de check-in.')
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    
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

    user_id = 1  # Exemple d'ID utilisateur, à remplacer par l'ID réel
    cursor.execute('''
        INSERT INTO Reservations (equipment_id, check_in, check_out, user_id)
        VALUES (?, ?, ?, ?)
    ''', (selected_equipment, check_in_date, check_out_date, user_id))
    conn.commit()
    
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    subject = "Confirmation de réservation d'équipement"
    body = f"Bonjour,\n\nVotre réservation pour l'équipement {selected_equipment} a été confirmée.\n\nDétails de la réservation:\nDate de début: {check_in_date}\nDate de fin: {check_out_date}\n\nMerci!"
    send_email_via_outlook(user_email, subject, body)
    
    messagebox.showinfo('Succès', 'Réservation réussie! Un email de confirmation a été envoyé.')

def cancel_reservation():
    selected_equipment = equipment_var.get()
    user_id = 1  # Exemple d'ID utilisateur, à remplacer par l'ID réel

    if not selected_equipment:
        messagebox.showerror('Erreur', 'Veuillez sélectionner un équipement à annuler.')
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Reservations 
        WHERE user_id = ? AND equipment_id = ?
    ''', (user_id, selected_equipment))
    
    if cursor.rowcount == 0:
        messagebox.showerror('Erreur', 'Aucune réservation trouvée pour cet utilisateur et cet équipement.')
        conn.close()
        return
    
    conn.commit()
    
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    subject = "Annulation de réservation d'équipement"
    body = f"Bonjour,\n\nVotre réservation pour l'équipement {selected_equipment} a été annulée.\n\nMerci!"
    send_email_via_outlook(user_email, subject, body)

    messagebox.showinfo('Succès', 'Réservation annulée! Un email de confirmation a été envoyé.')

def view_user_reservations():
    user_id = 1  # Exemple d'ID utilisateur, à remplacer par l'ID réel

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT equipment_id, check_in, check_out 
        FROM Reservations 
        WHERE user_id = ?
    ''', (user_id,))
    
    reservations = cursor.fetchall()
    conn.close()

    for row in tree.get_children():
        tree.delete(row)
    
    if reservations:
        for reservation in reservations:
            tree.insert("", "end", values=reservation)
    else:
        messagebox.showinfo("Information", "Aucune réservation trouvée pour cet utilisateur.")

def create_ui():
    global check_in_cal, check_out_cal, equipment_var, tree, availability_label

    create_tables()

    user_window = Tk()
    user_window.title('Réservation d\'équipement')
    user_window.geometry('1200x800')

    canvas = Canvas(user_window, width=600, height=700)
    canvas.pack(fill='both', expand=True)

    color1 = "#ADD8E6"  # bleu clair
    color2 = "#FFFFFF"  # blanc
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

    equipments = [f"Equipment {i+1}" for i in range(10)]  # Liste d'exemple d'équipements

    equipment_menu = OptionMenu(container, equipment_var, *equipments)
    equipment_menu.pack(pady=10)
    equipment_menu.config(width=20)

    # Affichage de disponibilité
    availability_label = Label(container, text="Sélectionnez un équipement et une date", bg='#ADD8E6', fg='black')
    availability_label.pack(pady=10)

    Label(container, text="Choisissez la date de check-in", bg='#ADD8E6', fg='black').pack(pady=10)
    check_in_cal = Calendar(container, selectmode='day', date_pattern='yyyy-mm-dd')
    check_in_cal.pack(pady=10)

    Label(container, text="Choisissez la date de check-out", bg='#ADD8E6', fg='black').pack(pady=10)
    check_out_cal = Calendar(container, selectmode='day', date_pattern='yyyy-mm-dd')
    check_out_cal.pack(pady=10)

    # Lorsque la date de check-in ou un équipement est sélectionné, vérifiez la disponibilité
    check_in_cal.bind("<<CalendarSelected>>", update_availability)
    equipment_var.trace('w', update_availability)

    book_button = Button(container, text="Réserver", command=book_equipment, bg='white', fg='black')
    book_button.pack(pady=20)

    cancel_button = Button(container, text="Annuler une réservation", command=cancel_reservation, bg='white', fg='black')
    cancel_button.pack(pady=20)

    view_button = Button(container, text="Voir les réservations de l'utilisateur", command=view_user_reservations, bg='white', fg='black')
    view_button.pack(pady=20)

    # Tableau des réservations
    columns = ("equipment_id", "check_in", "check_out")
    tree = ttk.Treeview(container, columns=columns, show="headings")
    tree.heading("equipment_id", text="ID de l'équipement")
    tree.heading("check_in", text="Date de check-in")
    tree.heading("check_out", text="Date de check-out")
    tree.pack(pady=20, fill='x')

    user_window.mainloop()

if __name__ == "__main__":
    create_ui()
