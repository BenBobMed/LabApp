from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
import win32com.client as win32
#from login import authenticated_id

# Function to send email via Outlook
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

    # Fetch total reservations per day
    cursor.execute('''
        SELECT DATE(res_Start), COUNT(DISTINCT Lab_ID) as count 
        FROM Resrvation_Lab 
        GROUP BY DATE(res_Start)
    ''')
    total_reservations = cursor.fetchall()

    conn.close()

    for res_date, res_count in total_reservations:
        # Determine color based on the number of total reservations
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

def book_equipment():
    selected_equipment = equipment_var.get()
    check_in_date = check_in_cal.get_date()
    check_out_date = check_out_cal.get_date()

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

    from login import authenticated_id
    user_id = authenticated_id  # Placeholder: Get the actual user ID
    cursor.execute('''
        INSERT INTO Reservations (equipment_id, check_in, check_out, user_id)
        VALUES (?, ?, ?, ?)
    ''', (selected_equipment, check_in_date, check_out_date, user_id))
    conn.commit()
    conn.close()
    
    # Fetch user's email
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    # Send email notification
    subject = "Confirmation de réservation d'équipement"
    body = f"Bonjour,\n\nVotre réservation pour l'équipement {selected_equipment} a été confirmée.\n\nDétails de la réservation:\nDate de début: {check_in_date}\nDate de fin: {check_out_date}\n\nMerci!"
    send_email_via_outlook(user_email, subject, body)
    
    messagebox.showinfo('Succès', 'Réservation réussie! Un email de confirmation a été envoyé.')
    update_calendar()

def cancel_reservation():
    user_id = simpledialog.askstring("ID de l'utilisateur", "Entrez l'ID de l'utilisateur:")
    if not user_id:
        return
    
    equipment_id = simpledialog.askstring("ID de l'équipement", "Entrez l'ID de l'équipement:")
    if not equipment_id:
        return

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Reservations 
        WHERE user_id = ? AND equipment_id = ?
    ''', (user_id, equipment_id))
    
    if cursor.rowcount == 0:
        messagebox.showerror('Erreur', 'Aucune réservation trouvée pour cet utilisateur et cet équipement.')
        conn.close()
        return
    
    conn.commit()
    conn.close()

    # Fetch user's email
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    # Send email notification
    subject = "Annulation de réservation d'équipement"
    body = f"Bonjour,\n\nVotre réservation pour l'équipement {equipment_id} a été annulée.\n\nMerci!"
    send_email_via_outlook(user_email, subject, body)

    messagebox.showinfo('Succès', 'Réservation annulée! Un email de confirmation a été envoyé.')
    update_calendar()

def view_user_reservations():
    user_id = simpledialog.askstring("ID de l'utilisateur", "Entrez l'ID de l'utilisateur:")
    if not user_id:
        return
    
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
    
    for reservation in reservations:
        tree.insert("", "end", values=reservation)

def create_ui():
    global cal, check_in_cal, check_out_cal, equipment_var, tree

    user_window = Tk()  # Initialize the main window
    user_window.title('Réservation d\'équipement')
    user_window.geometry('600x700')  # Increased height to accommodate the new elements

    # Create canvas for gradient background
    canvas = Canvas(user_window, width=600, height=700)
    canvas.pack(fill='both', expand=True)

    # Create gradient
    color1 = "#ADD8E6"  # lightblue
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

    # Place the widgets on top of the canvas
    container = Frame(user_window, bg='#ADD8E6')  # Set to light blue
    container.place(relwidth=1, relheight=1)

    equipment_var = StringVar()

    Label(container, text="Choisissez l'équipement", bg='#ADD8E6', fg='black').pack(pady=10)

    equipments = [f"Equipment {i+1}" for i in range(10)]  # Placeholder for actual equipment list

    equipment_menu = OptionMenu(container, equipment_var, *equipments)
    equipment_menu.pack(pady=10)
    equipment_menu.config(width=20)

    Label(container, text="Choisissez la date de check-in", bg='#ADD8E6', fg='black').pack(pady=10)
    check_in_cal = Calendar(container, selectmode='day', date_pattern='yyyy-mm-dd')
    check_in_cal.pack(pady=10)

    Label(container, text="Choisissez la date de check-out", bg='#ADD8E6', fg='black').pack(pady=10)
    check_out_cal = Calendar(container, selectmode='day', date_pattern='yyyy-mm-dd')
    check_out_cal.pack(pady=10)

    book_button = Button(container, text="Réserver", command=book_equipment, bg='white', fg='black')
    book_button.pack(pady=20)

    cancel_button = Button(container, text="Annuler une réservation", command=cancel_reservation, bg='white', fg='black')
    cancel_button.pack(pady=20)

    view_button = Button(container, text="Voir les réservations de l'utilisateur", command=view_user_reservations, bg='white', fg='black')
    view_button.pack(pady=20)

    # Create the Treeview (table) to display reservations
    columns = ("equipment_id", "check_in", "check_out")
    tree = ttk.Treeview(container, columns=columns, show="headings")
    tree.heading("equipment_id", text="ID de l'équipement")
    tree.heading("check_in", text="Date de check-in")
    tree.heading("check_out", text="Date de check-out")
    tree.pack(pady=20)

    user_window.mainloop()  # Start the main loop of the user window

# If this file is executed directly, create the UI
if __name__ == "__main__":
    create_ui()
