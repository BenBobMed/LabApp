from tkinter import *
from tkinter import messagebox
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
import win32com.client as win32

# Function to send an email via Outlook
def send_email_via_outlook(to, subject, body):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = subject
    mail.Body = body
    mail.Send()

def update_calendar():
    # Remove previous events
    cal.calevent_remove('all')

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    # Retrieve the total number of reservations per day
    cursor.execute('''
        SELECT DATE(res_Start), COUNT(DISTINCT Lab_ID) as count 
        FROM Resrvation_Lab 
        GROUP BY DATE(res_Start)
    ''')
    total_reservations = cursor.fetchall()

    conn.close()

    for res_date, res_count in total_reservations:
        # Determine the color based on the number of reservations
        if res_count == 1:
            color = 'green'
        elif res_count == 2:
            color = 'blue'
        elif res_count == 3:
            color = 'orange'
        elif res_count >= 4:
            color = 'red'

        # Create a unique tag for each date
        tag_name = f"res_dot_{res_date}"
        cal.calevent_create(datetime.strptime(res_date, '%Y-%m-%d'), '', tag_name)
        # Set the color for the tag
        cal.tag_config(tag_name, background=color)

def display_date_details(event):
    selected_date = cal.get_date()
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Lab_ID, res_Start, res_End
        FROM Resrvation_Lab
        WHERE DATE(res_Start) = ?
    ''', (selected_date,))
    reservations = cursor.fetchall()

    conn.close()

    # Prepare the information to display
    if reservations:
        details = f"Réservations pour le {selected_date}:\n\n"
        for lab_id, res_start, res_end in reservations:
            details += f"Lab ID: {lab_id}\nDébut: {res_start}\nFin: {res_end}\n\n"
    else:
        details = f"Aucune réservation pour le {selected_date}."

    # Display the details in a dialog box
    messagebox.showinfo("Détails des Réservations", details)

def book_lab():
    selected_lab_id = lab_id_var.get()
    selected_date = cal.get_date()
    time_slot = time_slot_var.get()

    # Determine the start and end time based on the selected time slot
    if time_slot == "08:00 - 12:00":
        start_time = f"{selected_date} 08:00:00"
        end_time = f"{selected_date} 12:00:00"
    elif time_slot == "14:00 - 18:00":
        start_time = f"{selected_date} 14:00:00"
        end_time = f"{selected_date} 18:00:00"
    else:
        messagebox.showerror('Erreur', 'Veuillez sélectionner un créneau horaire valide')
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Resrvation_Lab
        WHERE Lab_ID = ? AND (
            (res_Start < ? AND res_End > ?) OR
            (res_Start < ? AND res_End > ?)
        )
    ''', (selected_lab_id, end_time, start_time, start_time, end_time))
    
    if cursor.fetchone():
        conn.close()
        messagebox.showerror('Erreur', 'Ce créneau est déjà réservé.')
        return

    user_id = 1  # Placeholder: Get the actual user ID
    cursor.execute('''
        INSERT INTO Resrvation_Lab (Lab_ID, res_Start, res_End, user_id)
        VALUES (?, ?, ?, ?)
    ''', (selected_lab_id, start_time, end_time, user_id))
    conn.commit()
    conn.close()
    
    # Retrieve the user's email
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM data WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    # Send a notification email
    subject = "Confirmation de Réservation de Laboratoire"
    body = f"Bonjour,\n\nVotre réservation pour le laboratoire ID {selected_lab_id} a été confirmée.\n\nDétails de la réservation:\nDate: {selected_date}\nCréneau horaire: {time_slot}\n\nMerci!"
    send_email_via_outlook(user_email, subject, body)
    
    messagebox.showinfo('Succès', 'Réservation réussie! Un e-mail de confirmation a été envoyé.')
    update_calendar()

def cancel_reservation():
    selected_lab_id = lab_id_var.get()
    selected_date = cal.get_date()
    time_slot = time_slot_var.get()

    # Determine the start and end time based on the selected time slot
    if time_slot == "08:00 - 12:00":
        start_time = f"{selected_date} 08:00:00"
        end_time = f"{selected_date} 12:00:00"
    elif time_slot == "14:00 - 18:00":
        start_time = f"{selected_date} 14:00:00"
        end_time = f"{selected_date} 18:00:00"
    else:
        messagebox.showerror('Erreur', 'Veuillez sélectionner un créneau horaire valide')
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Resrvation_Lab
        WHERE Lab_ID = ? AND res_Start = ? AND res_End = ?
    ''', (selected_lab_id, start_time, end_time))
    
    if cursor.rowcount == 0:
        conn.close()
        messagebox.showerror('Erreur', 'Aucune réservation trouvée pour ce créneau.')
        return

    conn.commit()
    conn.close()

    # Retrieve the user's email
    user_id = 1  # Placeholder: Get the actual user ID
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM data WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    # Send a notification email
    subject = "Annulation de Réservation de Laboratoire"
    body = f"Bonjour,\n\nVotre réservation pour le laboratoire ID {selected_lab_id} le {selected_date} durant le créneau horaire {time_slot} a été annulée.\n\nMerci!"
    send_email_via_outlook(user_email, subject, body)
    
    messagebox.showinfo('Succès', 'Réservation annulée! Un e-mail de confirmation a été envoyé.')
    update_calendar()

def create_ui():
    global lab_id_var, cal, time_slot_var, labs

    user_window = Tk()  # Initialize the main window
    user_window.title('Réservation de Laboratoire')
    user_window.geometry('800x1000')  # Increase window size to accommodate enlarged elements

    lab_id_var = StringVar()
    time_slot_var = StringVar()

    Label(user_window, text="Choisissez le laboratoire").pack(pady=10)

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Lab_ID FROM Lab WHERE Lab_ID != 5')  # Exclude Lab 5
    labs = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not labs:
        messagebox.showwarning('Avertissement', 'Aucun laboratoire disponible')
        user_window.destroy()
        return

    lab_menu = OptionMenu(user_window, lab_id_var, *labs)
    lab_menu.pack(pady=10)
    lab_menu.config(width=20)
    Label(user_window, text="(Sélectionnez un laboratoire pour voir les réservations)").pack(pady=5)

    Label(user_window, text="Choisissez la date").pack(pady=10)
    cal = Calendar(user_window, selectmode='day', date_pattern='yyyy-mm-dd', font=('Arial', 12))  # Increase font size
    cal.pack(pady=10, padx=10)  # Add padding for more space around the calendar

    Label(user_window, text="Choisissez le créneau horaire").pack(pady=10)
    time_slot_menu = OptionMenu(user_window, time_slot_var, "08:00 - 12:00", "14:00 - 18:00")
    time_slot_menu.pack(pady=10)
    time_slot_menu.config(width=20)

    book_button = Button(user_window, text="Réserver", command=book_lab)
    book_button.pack(pady=20)

    cancel_button = Button(user_window, text="Annuler la réservation", command=cancel_reservation)
    cancel_button.pack(pady=20)

    cal.bind("<<CalendarSelected>>", display_date_details)

    # Color legend with enlarged elements
    legend_frame = Frame(user_window, borderwidth=2, relief="groove")
    legend_frame.pack(pady=20, padx=10, fill='x')

    Label(legend_frame, text="Légende des couleurs", font=('Arial', 14, 'bold')).pack(pady=10)  # Increased font size
    Label(legend_frame, text="Vert: 1 réservation", bg='green', font=('Arial', 12), width=20).pack(pady=5)  # Increased font size
    Label(legend_frame, text="Bleu: 2 réservations", bg='blue', font=('Arial', 12), width=20).pack(pady=5)  # Increased font size
    Label(legend_frame, text="Orange: 3 réservations", bg='orange', font=('Arial', 12), width=20).pack(pady=5)  # Increased font size
    Label(legend_frame, text="Rouge: 4 réservations ou plus", bg='red', font=('Arial', 12), width=20).pack(pady=5)  # Increased font size

    update_calendar()

    # Add color legend
    legend_frame = Frame(user_window)
    legend_frame.pack(pady=20)

    Label(legend_frame, text="Legend:").grid(row=0, column=0, sticky=W, padx=10)

    colors = {
        'green': '1 Lab Reserved',
        'blue': '2 Labs Reserved',
        'orange': '3 Labs Reserved',
        'red': '4 Labs Reserved'
    }

    col = 1
    for color, description in colors.items():
        Label(legend_frame, text=description, bg=color, width=20).grid(row=0, column=col, pady=5, padx=10, sticky=W)
        col += 1

    user_window.mainloop()  # Renamed from root.mainloop() to user_window.mainloop()

create_ui()
