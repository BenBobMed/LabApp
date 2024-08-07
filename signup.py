from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import sqlite3
import os
import re  # Import regex module for password validation

def connect_database():
    email = emailEntry.get()
    password = passwordEntry.get()
    username = UsernameEntry.get()
    confirm_password = ConfirmEntry.get()
#test
    if email == '' or password == '' or username == '' or confirm_password == '':
        messagebox.showerror('Erreur', 'Veuillez saisir vos informations')
    elif not email.endswith('@capgemini.com'):  # Check if email ends with '@capgemini.com'
        messagebox.showerror('Erreur', "Vous devez entrer un email '@capgemini.com'")
    elif password != confirm_password:
        messagebox.showerror('Erreur', "Votre mot de passe n'est pas compatible")
    elif check.get() == 0:
        messagebox.showerror('Erreur', "Veuillez accepter les règles et les conditions")
    elif not validate_password(password):  # Check if the password is strong
        messagebox.showerror('Erreur', "Le mot de passe doit être fort (au moins 8 caractères, incluant lettres majuscules, minuscules, chiffres et caractères spéciaux)")
    else:
        try:
            conn = sqlite3.connect('userdata.db')
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT NOT NULL,
                            utilisateur TEXT NOT NULL,
                            password TEXT NOT NULL,  -- Added missing comma here
                            is_admin INTEGER DEFAULT 0
                        )''')

            c.execute('INSERT INTO data (email, utilisateur, password) VALUES (?, ?, ?)',
                      (email, username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo('Succès', 'Inscription réussie')
        except Exception as e:
            messagebox.showerror('Erreur', f"Erreur de la base de données: {str(e)}")

def validate_password(password):
    """Validates the password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False
    return True

def login_page():
    signup_window.destroy()
    import login  # Assurez-vous que ce module existe et est dans le bon répertoire

signup_window = Tk()
signup_window.title("Sign Up")
signup_window.resizable(False, False)

# Get the directory of the current script
current_dir = os.path.dirname(__file__)

# Construct the relative path to the image
image_path = os.path.join(current_dir, 'bgn.jpg')
background = ImageTk.PhotoImage(Image.open(image_path))

bgLabel = Label(signup_window, image=background)
bgLabel.grid()

frame = Frame(signup_window, bg='white')
frame.place(x=590, y=35)

heading = Label(frame, text='Créer un compte', font=('Microsoft Yahei UI Light', 23, 'bold'), bg='white', fg='blue4')
heading.grid(row=0, column=0, padx=10, pady=10)

UsernameLabel = Label(frame, text="Nom d'utilisateur", font=('Microsoft Yahei UI Light', 15, 'bold'), bg='white', fg='blue4')
UsernameLabel.grid(row=1, column=0, sticky='w', padx=5, pady=(5, 0))

UsernameEntry = Entry(frame, width=40, font=('Microsoft Yahei UI Light', 10, 'bold'), fg='white', bg='blue4')
UsernameEntry.grid(row=2, column=0, sticky='w', padx=5)

emailLabel = Label(frame, text='Email', font=('Microsoft Yahei UI Light', 15, 'bold'), bg='white', fg='blue4')
emailLabel.grid(row=3, column=0, sticky='w', padx=5, pady=(10, 0))

emailEntry = Entry(frame, width=40, font=('Microsoft Yahei UI Light', 10, 'bold'), fg='white', bg='blue4')
emailEntry.grid(row=4, column=0, sticky='w', padx=5)

passwordLabel = Label(frame, text='Mot de passe', font=('Microsoft Yahei UI Light', 15, 'bold'), bg='white', fg='blue4')
passwordLabel.grid(row=5, column=0, sticky='w', padx=5, pady=(10, 0))

passwordEntry = Entry(frame, width=40, font=('Microsoft Yahei UI Light', 10, 'bold'), fg='white', bg='blue4', show='*')
passwordEntry.grid(row=6, column=0, sticky='w', padx=5)

ConfirmLabel = Label(frame, text='Confirmer votre mot de passe', font=('Microsoft Yahei UI Light', 15, 'bold'), bg='white', fg='blue4')
ConfirmLabel.grid(row=7, column=0, sticky='w', padx=5, pady=(10, 0))

ConfirmEntry = Entry(frame, width=40, font=('Microsoft Yahei UI Light', 10, 'bold'), fg='white', bg='blue4', show='*')
ConfirmEntry.grid(row=8, column=0, sticky='w', padx=5)

check = IntVar()
termsandconditions = Checkbutton(frame, text="J'accèpte les règles et les conditions", font=('Microsoft Yahei UI Light', 8, 'bold'),
                                 fg='blue4', bg='white', activebackground='white', activeforeground='blue4',
                                 cursor='hand2', variable=check)
termsandconditions.grid(row=9, column=0, sticky='w', padx=50, pady=(10))

signupButton = Button(frame, text='Signup', font=('Open Sans', 16, 'bold'), bd=0, bg='blue4', fg='white',
                      activebackground='white', activeforeground='blue4', cursor='hand2', width=17, command=connect_database)
signupButton.grid(row=10, column=0, padx=5, pady=5)

alreadyaccount = Label(frame, text="Vous avez un compte?", font=('Open Sans', 9, 'bold'), bg='white', fg='blue4')
alreadyaccount.grid(row=11, column=0, sticky='w', padx=5, pady=10)

loginButton = Button(frame, text='Log in', font=('Open Sans', 9, 'bold underline'), bd=0, bg='blue4', fg='white',
                     cursor='hand2', activebackground='white', activeforeground='blue4', command=login_page)
loginButton.place(x=150, y=427)

signup_window.mainloop()