from tkinter import *
from tkinter import messagebox
import sqlite3
from datetime import datetime

def book_lab():
    selected_lab_id = lab_id_var.get()
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()

    # Validate input times
    if not selected_lab_id or not start_time or not end_time:
        messagebox.showerror('Erreur', 'Veuillez remplir tous les champs')
        return

    try:
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        messagebox.showerror('Erreur', 'Format de date invalide. Utilisez YYYY-MM-DD HH:MM:SS.')
        return

    if (end_time - start_time).total_seconds() != 4 * 3600:
        messagebox.showerror('Erreur', 'La réservation doit durer exactement 4 heures.')
        return

    # Check if the reservation conflicts with existing ones
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

    # Insert the reservation
    user_id = 1  # Placeholder: Get the actual user ID
    cursor.execute('''
        INSERT INTO Resrvation_Lab (Lab_ID, res_Start, res_End, user_id)
        VALUES (?, ?, ?, ?)
    ''', (selected_lab_id, start_time, end_time, user_id))
    conn.commit()
    conn.close()
    messagebox.showinfo('Succès', 'Réservation réussie!')

def create_ui():
    global lab_id_var, start_time_entry, end_time_entry
    
    root = Tk()
    root.title('Réservation de Laboratoire')
    root.geometry('400x300')
    
    lab_id_var = StringVar()
    
    Label(root, text="Choisissez le laboratoire").pack(pady=10)
    
    # Fetch lab options from the database
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Lab_ID FROM Lab')
    labs = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not labs:
        messagebox.showwarning('Avertissement', 'Aucun laboratoire disponible')
        root.destroy()
        return
    
    lab_menu = OptionMenu(root, lab_id_var, *labs)
    lab_menu.pack(pady=10)
    
    Label(root, text="Heure de début (YYYY-MM-DD HH:MM:SS)").pack(pady=5)
    start_time_entry = Entry(root)
    start_time_entry.pack(pady=5)
    
    Label(root, text="Heure de fin (YYYY-MM-DD HH:MM:SS)").pack(pady=5)
    end_time_entry = Entry(root)
    end_time_entry.pack(pady=5)
    
    book_button = Button(root, text="Réserver", command=book_lab)
    book_button.pack(pady=20)
    
    root.mainloop()

create_ui()
