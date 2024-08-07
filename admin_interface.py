from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import sqlite3
import os

def add_is_admin_column():
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
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

add_is_admin_column()

def edit_users():
    for widget in table_frame.winfo_children():
        widget.destroy()
    
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, utilisateur, email, is_admin FROM data")
    users = cursor.fetchall()
    conn.close()
    
    user_table = ttk.Treeview(table_frame, columns=('ID', 'Username', 'Email', 'Is Admin'), show='headings')
    user_table.heading('ID', text='ID')
    user_table.heading('Username', text='Username')
    user_table.heading('Email', text='Email')
    user_table.heading('Is Admin', text='Admin')
    
    for user in users:
        user_table.insert('', END, values=user)
    
    user_table.pack(expand=True, fill='both')
    
    make_admin_btn = Button(table_frame, text="Toggle Admin", command=lambda: make_admin(user_table))
    make_admin_btn.pack(pady=10)

def make_admin(user_table):
    selected_item = user_table.selection()
    if selected_item:
        user_id = user_table.item(selected_item)['values'][0]
        is_admin = user_table.item(selected_item)['values'][3]
        new_admin_status = not is_admin
        
        conn = sqlite3.connect('userdata.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE data SET is_admin = ? WHERE id = ?", (new_admin_status, user_id))
        conn.commit()
        conn.close()
        
        user_table.item(selected_item, values=(*user_table.item(selected_item)['values'][:3], new_admin_status))
        
        messagebox.showinfo('Success', f"Admin status for user ID {user_id} has been updated.")

def edit_product():
    edit_window = Toplevel(admin_window)
    edit_window.title("Edit Product")
    edit_window.geometry('300x200')

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
            
            cursor.execute('SELECT * FROM Mat WHERE mat_ref = ?', (mat_ref,))
            if cursor.fetchone():
                cursor.execute('UPDATE Mat SET mat_categ = ?, mat_Qte = ? WHERE mat_ref = ?', (mat_categ, mat_qte, mat_ref))
            else:
                cursor.execute('INSERT INTO Mat (mat_ref, mat_categ, mat_Qte) VALUES (?, ?, ?)', (mat_ref, mat_categ, mat_qte))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Product details saved.")
            edit_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields correctly.")

    save_button = Button(edit_window, text="Save", command=save_product)
    save_button.pack(pady=10)

def check_assets():
    for widget in table_frame.winfo_children():
        widget.destroy()
    
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
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
    
    tree = ttk.Treeview(table_frame, columns=('Mat_ID', 'Start Time', 'End Time', 'User ID'), show='headings')
    tree.heading('Mat_ID', text='Mat ID')
    tree.heading('Start Time', text='Start Time')
    tree.heading('End Time', text='End Time')
    tree.heading('User ID', text='User ID')
    
    for result in results:
        tree.insert('', 'end', values=result)
    
    tree.pack(expand=True, fill='both')

def check_lab():
    for widget in table_frame.winfo_children():
        widget.destroy()

    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()

    try:
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

        lab_table = ttk.Treeview(table_frame, columns=('Lab_ID', 'Start Time', 'End Time', 'User'), show='headings')
        lab_table.heading('Lab_ID', text='Lab_ID')
        lab_table.heading('Start Time', text='Start Time')
        lab_table.heading('End Time', text='End Time')
        lab_table.heading('User', text='User')

        for lab in labs:
            lab_table.insert('', END, values=lab)

        lab_table.pack(expand=True, fill='both')

    finally:
        conn.close()

def search():
    search_text = search_entry.get()
    search_type = search_combobox.get()
    print(f"Searching for '{search_text}' in '{search_type}'")

admin_window = Tk()
admin_window.title("Admin Interface")
admin_window.geometry('1000x600')

current_dir = os.path.dirname(__file__)
image_path = os.path.join(current_dir, 'bgn.jpg')
background = ImageTk.PhotoImage(Image.open(image_path))
bg_label = Label(admin_window, image=background)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Coordinates calculated to fit within the white area of the background image
button_frame = Frame(admin_window, bg='white')
button_frame.place(x=350, y=120, width=300, height=350)  # Adjust these values to fit within the white area

edit_users_btn = Button(button_frame, text="Edit users", command=edit_users)
edit_users_btn.place(x=75, y=20, width=150, height=40)  # Adjusted positions

edit_product_btn = Button(button_frame, text="Edit product", command=edit_product)
edit_product_btn.place(x=75, y=70, width=150, height=40)  # Adjusted positions

check_assets_btn = Button(button_frame, text="Check assets", command=check_assets)
check_assets_btn.place(x=75, y=120, width=150, height=40)  # Adjusted positions

check_lab_btn = Button(button_frame, text="Check lab", command=check_lab)
check_lab_btn.place(x=75, y=170, width=150, height=40)  # Adjusted positions

search_entry = Entry(button_frame)
search_entry.place(x=25, y=220, width=200, height=30)  # Adjusted positions

search_combobox = ttk.Combobox(button_frame, values=["Users", "Products", "Assets", "Labs"])
search_combobox.place(x=25, y=260, width=200, height=30)  # Adjusted positions
search_combobox.current(0)

search_button = Button(button_frame, text="Search", command=search)
search_button.place(x=75, y=300, width=150, height=30)  # Adjusted positions

table_frame = Frame(admin_window, bg='white')
table_frame.place(x=20, y=500, width=960, height=80)  # Adjusted positions

admin_window.mainloop()
