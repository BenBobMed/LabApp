
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
    
    # Create a new top-level window
    edit_window = Toplevel(admin_window)
    edit_window.title("Edit Product")
    edit_window.geometry('300x200')

    # Create labels and entry fields for asset details
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
            
            # Check if the product already exists
            cursor.execute('SELECT * FROM Mat WHERE mat_ref = ?', (mat_ref,))
            if cursor.fetchone():
                # Update existing product
                cursor.execute('UPDATE Mat SET mat_categ = ?, mat_Qte = ? WHERE mat_ref = ?', (mat_categ, mat_qte, mat_ref))
            else:
                # Insert new product
                cursor.execute('INSERT INTO Mat (mat_ref, mat_categ, mat_Qte) VALUES (?, ?, ?)', (mat_ref, mat_categ, mat_qte))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Product details saved.")
            edit_window.destroy()  # Close the window after saving
        else:
            messagebox.showwarning("Input Error", "Please fill all fields correctly.")

    # Save button
    save_button = Button(edit_window, text="Save", command=save_product)
    save_button.pack(pady=10)

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

# Set the background color to blue
admin_window.configure(bg='blue')

# Buttons for different admin actions
button_frame = Frame(admin_window, bg='blue', bd=0)
button_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

edit_users_btn = Button(button_frame, text="Edit users", command=edit_users, width=20)
edit_users_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

edit_product_btn = Button(button_frame, text="Edit product", command=edit_product, width=20)
edit_product_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

check_assets_btn = Button(button_frame, text="Check Assets", command=check_assets, width=20)
check_assets_btn.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

check_lab_btn = Button(button_frame, text="Check Labo", command=check_lab, width=20)
check_lab_btn.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

# Search section
search_frame = Frame(admin_window, bg='blue', bd=0)
search_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky='ew')

search_entry = Entry(search_frame, width=30)
search_entry.grid(row=0, column=0, padx=5, pady=5)
search_entry.insert(0, "Search by name")

search_combobox = ttk.Combobox(search_frame, values=["User", "Lab", "Asset"])
search_combobox.grid(row=0, column=1, padx=5, pady=5)
search_combobox.set("Select item")

search_button = Button(search_frame, text="Search", command=search)
search_button.grid(row=0, column=2, padx=5, pady=5)

# Area where the tables will be shown
table_frame = Frame(admin_window, width=900, height=300, bg='white', relief=RIDGE, bd=2)
table_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

# Make sure the layout adjusts when the window is resized
admin_window.grid_rowconfigure(2, weight=1)
admin_window.grid_columnconfigure(0, weight=1)
admin_window.grid_columnconfigure(1, weight=1)
admin_window.grid_columnconfigure(2, weight=1)
admin_window.grid_columnconfigure(3, weight=1)

admin_window.mainloop()
