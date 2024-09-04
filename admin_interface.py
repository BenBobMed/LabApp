from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import os
 
def add_is_admin_column():
    # Connect to the database
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
   
    # Check if the 'is_admin' column exists
    try:
        cursor.execute("PRAGMA table_info(data)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'is_admin' not in columns:
            cursor.execute("ALTER TABLE data ADD COLUMN is_admin INTEGER DEFAULT 0")
            conn.commit()
            print("Column 'is_admin' added successfully.")
        else:
            print("Column 'is_admin' already exists.")
    except sqlite3.OperationalError as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
 
# Run the function to add the column
add_is_admin_column()
 
def edit_users():
    # Clear any previous widgets from table_frame
    for widget in table_frame.winfo_children():
        widget.destroy()
   
    # Fetch users from database
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, utilisateur, email, is_admin FROM data")
    users = cursor.fetchall()
    conn.close()
   
    # Display the users in a Treeview (like a table)
    user_table = ttk.Treeview(table_frame, columns=('ID', 'Username', 'Email', 'Is Admin'), show='headings')
    user_table.heading('ID', text='ID')
    user_table.heading('Username', text='Username')
    user_table.heading('Email', text='Email')
    user_table.heading('Is Admin', text='Admin')
   
    # Insert users into the table
    for user in users:
        user_table.insert('', END, values=user)
   
    user_table.pack(expand=True, fill='both')
   
    # Button to toggle admin rights
    make_admin_btn = Button(table_frame, text="Toggle Admin", command=lambda: make_admin(user_table))
    make_admin_btn.pack(pady=10)
 
def make_admin(user_table):
    selected_item = user_table.selection()
    if selected_item:
        user_id = user_table.item(selected_item)['values'][0]
        is_admin = user_table.item(selected_item)['values'][3]
        new_admin_status = not is_admin  # Toggle admin status
       
        # Update the database
        conn = sqlite3.connect('userdata.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE data SET is_admin = ? WHERE id = ?", (new_admin_status, user_id))
        conn.commit()
        conn.close()
       
        # Update the table display
        user_table.item(selected_item, values=(*user_table.item(selected_item)['values'][:3], new_admin_status))
       
        messagebox.showinfo('Success', f"Admin status for user ID {user_id} has been updated.")
 
def edit_product():
    # Créer une nouvelle fenêtre pour l'édition de produit
    edit_window = Toplevel(admin_window)
    edit_window.title("Edit Product")
    edit_window.geometry('300x200')
 
    # Créer les champs pour entrer les détails du produit
    Label(edit_window, text="Asset Reference:").pack(pady=5)
    mat_ref_entry = Entry(edit_window)
    mat_ref_entry.pack(pady=5)
 
    Label(edit_window, text="Category:").pack(pady=5)
    mat_categ_entry = Entry(edit_window)
    mat_categ_entry.pack(pady=5)
 
    Label(edit_window, text="Quantity:").pack(pady=5)
    mat_qte_entry = Entry(edit_window)
    mat_qte_entry.pack(pady=5)
 
    def save_product():
        mat_ref = mat_ref_entry.get()
        mat_categ = mat_categ_entry.get()
        try:
            mat_qte = int(mat_qte_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a number.")
            return
 
        if mat_ref and mat_categ and mat_qte >= 0:
            conn = sqlite3.connect('userdata.db')
            cursor = conn.cursor()
 
            # Vérifier si le produit existe déjà
            cursor.execute('SELECT * FROM Mat WHERE mat_ref = ?', (mat_ref,))
            if cursor.fetchone():
                # Mettre à jour le produit existant
                cursor.execute('UPDATE Mat SET mat_categ = ?, mat_Qte = ? WHERE mat_ref = ?', (mat_categ, mat_qte, mat_ref))
            else:
                # Insérer un nouveau produit
                cursor.execute('INSERT INTO Mat (mat_ref, mat_categ, mat_Qte) VALUES (?, ?, ?)', (mat_ref, mat_categ, mat_qte))
 
            conn.commit()
            conn.close()
 
            messagebox.showinfo("Success", "Product details saved.")
            edit_window.destroy()  # Fermer la fenêtre après sauvegarde
        else:
            messagebox.showwarning("Input Error", "Please fill all fields correctly.")
 
    # Bouton pour sauvegarder les produits
    save_button = Button(edit_window, text="Save", command=save_product)
    save_button.pack(pady=10)
 
    # Bouton pour afficher tous les produits
    show_products_button = Button(edit_window, text="Show All Products", command=show_products)
    show_products_button.pack(pady=10)
 
def show_products():
    # Créer une nouvelle fenêtre pour afficher les produits
    products_window = Toplevel(admin_window)
    products_window.title("All Products")
    products_window.geometry('400x300')
 
    # Connexion à la base de données
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
 
    # Récupérer tous les produits
    cursor.execute("SELECT mat_ref, mat_categ, mat_Qte FROM Mat")
    products = cursor.fetchall()
    conn.close()
 
    # Créer un Treeview pour afficher les produits
    products_table = ttk.Treeview(products_window, columns=('Reference', 'Category', 'Quantity'), show='headings')
    products_table.heading('Reference', text='Reference')
    products_table.heading('Category', text='Category')
    products_table.heading('Quantity', text='Quantity')
 
    # Insérer les produits dans le tableau
    for product in products:
        products_table.insert('', END, values=product)
 
    products_table.pack(expand=True, fill='both')
 
def check_assets():
    # Clear any previous widgets from table_frame
    for widget in table_frame.winfo_children():
        widget.destroy()
   
    # Connect to the database
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
 
    # Query to get Mat_ID and the latest reservation details
    query = '''
    SELECT m.mat_ref, r.res_Start, r.res_End, r.user_id
    FROM Mat m
    LEFT JOIN (
        SELECT mat_ref, res_Start, res_End, user_id
        FROM Resrvation_Mat
        WHERE (mat_ref, res_Start) IN (
            SELECT mat_ref, MAX(res_Start)
            FROM Resrvation_Mat
            GROUP BY mat_ref
        )
    ) r ON m.mat_ref = r.mat_ref
    '''
   
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
   
    # Create and configure Treeview to display the results
    tree = ttk.Treeview(table_frame, columns=('Mat_ID', 'Start Time', 'End Time', 'User ID'), show='headings')
    tree.heading('Mat_ID', text='Mat ID')
    tree.heading('Start Time', text='Start Time')
    tree.heading('End Time', text='End Time')
    tree.heading('User ID', text='User ID')
   
    for result in results:
        tree.insert('', 'end', values=result)
   
    tree.pack(expand=True, fill='both')
 
def check_lab():
    # Clear any previous widgets from table_frame
    for widget in table_frame.winfo_children():
        widget.destroy()
 
    # Connect to the database
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
 
    try:
        # Query to get the latest reservation for each Lab_ID
        query = '''
        SELECT l.Lab_ID, r.res_Start, r.res_End, d.utilisateur
        FROM Lab l
        LEFT JOIN Resrvation_Lab r ON l.Lab_ID = r.Lab_ID
        LEFT JOIN data d ON r.user_id = d.id
        WHERE r.res_Start = (
            SELECT MAX(res_Start)
            FROM Resrvation_Lab
            WHERE Lab_ID = l.Lab_ID
        )
        '''
        cursor.execute(query)
        labs = cursor.fetchall()
 
        # Display the results in a Treeview
        lab_table = ttk.Treeview(table_frame, columns=('Lab_ID', 'Start Time', 'End Time', 'User'), show='headings')
        lab_table.heading('Lab_ID', text='Lab_ID')
        lab_table.heading('Start Time', text='Start Time')
        lab_table.heading('End Time', text='End Time')
        lab_table.heading('User', text='User')
 
        # Insert data into the table
        for lab in labs:
            lab_table.insert('', END, values=lab)
 
        lab_table.pack(expand=True, fill='both')
 
    finally:
        conn.close()
 
def search():
    search_text = search_entry.get()
    search_type = search_combobox.get()
    print(f"Searching for '{search_text}' in '{search_type}'")
 
# Main window
admin_window = Tk()
admin_window.title("Admin Interface")
admin_window.geometry('1000x600')  # Adjusted size for better layout
 
# Set the window icon if needed
# admin_window.iconbitmap('path_to_icon.ico')
 
# Sidebar for navigation
sidebar = Frame(admin_window, bg='lightgray', width=200)
sidebar.pack(fill='y', side='left')
 
# Table frame for displaying different tables
table_frame = Frame(admin_window, bg='white')
table_frame.pack(fill='both', expand=True, padx=20, pady=20)
 
# Add navigation buttons
Button(sidebar, text="Edit Users", command=edit_users, anchor='w').pack(fill='x')
Button(sidebar, text="Edit Product", command=edit_product, anchor='w').pack(fill='x')
Button(sidebar, text="Check Assets", command=check_assets, anchor='w').pack(fill='x')
Button(sidebar, text="Check Labs", command=check_lab, anchor='w').pack(fill='x')
 
# Search bar for quick access
search_frame = Frame(admin_window, bg='white')
search_frame.pack(fill='x', padx=20, pady=10)
 
search_entry = Entry(search_frame, width=50)
search_entry.pack(side='left', padx=10)
 
search_combobox = ttk.Combobox(search_frame, values=["Users", "Products", "Assets", "Labs"])
search_combobox.current(0)
search_combobox.pack(side='left')
 
search_button = Button(search_frame, text="Search", command=search)
search_button.pack(side='left', padx=10)
 
admin_window.mainloop()
 
 