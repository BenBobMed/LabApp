from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
import sqlite3

# Global variable to store authenticated email
authenticated_email = None
authenticated_id=None

# Functionality Part
def validate_login():
    global authenticated_email
    global authenticated_id
    entered_email = usernameEntry.get()
    entered_password = passwordEntry.get()

    # Connect to the database
    conn = sqlite3.connect('userdata.db')
    cursor = conn.cursor()
    
    # Query to fetch user with the provided email and password
    cursor.execute('SELECT * FROM data WHERE email = ? AND password = ?', (entered_email, entered_password))
    result = cursor.fetchone()
    
    conn.close()
    
    if result is None:
        messagebox.showerror('Erreur', 'Email ou mot de passe incorrect. Veuillez réessayer.')
    else:
        user_id, email, utilisateur, password, is_admin = result
        authenticated_email = email  # Store the authenticated email
        authenticated_id=user_id
        messagebox.showinfo('Succès', f'Connexion réussie! Votre email est: {authenticated_email}')
        #login_window.destroy()
        
        # Here, you can add functionality to open different windows based on the role
        if is_admin:
            login_window.destroy()
            import admin_interface  # Replace this with actual code to load admin interface
            admin_interface.show_admin_window()  # Assuming this is a function to show the admin window
        else:
             login_window.destroy()
             import materiel
             materiel.create_ui()  # Ensure this matches the actual function name in your codes a function to show the user window

# GUI Part
def user_enter(event):
    if usernameEntry.get() == 'Email':
        usernameEntry.delete(0, END)

def password_enter(event):
    if passwordEntry.get() == 'Password':
        passwordEntry.delete(0, END)

def hide():
    eyes.config(file='closeeyes.png')
    passwordEntry.config(show='')
    eyeButton.config(command=show)

def show():
    eyes.config(file='eyes.png')
    passwordEntry.config(show='*')
    eyeButton.config(command=hide)

def signup_page():
    login_window.destroy()
    import signup  # Replace this with actual signup code

login_window = Tk()
login_window.geometry('990x550+50+50')
login_window.resizable(False, False)
login_window.title('Login Page')
bgImage = ImageTk.PhotoImage(file='bgn.jpg')

bgLabel = Label(login_window, image=bgImage)
bgLabel.pack()

heading = Label(login_window, text='USER LOGIN', font=('Microsoft Yahei UI Light', 25, 'bold'), bg='white', fg='blue4')
heading.place(x=660, y=40)

usernameEntry = Entry(login_window, width=25, font=('Microsoft Yahei UI Light', 15, 'bold'), bd=0, fg='blue4')
usernameEntry.place(x=605, y=120)
usernameEntry.insert(0, 'Email')

usernameEntry.bind('<FocusIn>', user_enter)

frame1 = Frame(login_window, width=350, height=2, bg='blue4')
frame1.place(x=605, y=150)

passwordEntry = Entry(login_window, width=25, font=('Microsoft Yahei UI Light', 15, 'bold'), bd=0, fg='blue4')
passwordEntry.place(x=605, y=200)
passwordEntry.insert(0, 'Password')

passwordEntry.bind('<FocusIn>', password_enter)

frame2 = Frame(login_window, width=350, height=2, bg='blue4')
frame2.place(x=605, y=230)

eyes = PhotoImage(file='eyes.png')
eyeButton = Button(login_window, image=eyes, bd=0, bg='white', activebackground='white', cursor='hand2', command=hide)
eyeButton.place(x=930, y=210)

forgetButton = Button(login_window, text='Mot de passe oublié?', bd=0, bg='white', activebackground='white',
                      cursor='hand2', font=('Microsoft Yahei UI Light', 9, 'bold'),
                      fg='blue4', activeforeground='blue4')
forgetButton.place(x=810, y=235)

loginButton = Button(login_window, text='Login', font=('open Sans', 16, 'bold'), fg='white', bg='blue4',
                     activeforeground='white', activebackground='blue4', cursor='hand2', bd=0, width=25,
                     command=validate_login)
loginButton.place(x=610, y=290)

orLabel = Label(login_window, text='----------------------OR----------------------', font=('Open Sans', 16), fg='blue4', bg='white')
orLabel.place(x=610, y=340)

outlook_logo = PhotoImage(file='outlook.png')
outlookLabel = Label(login_window, image=outlook_logo, bg='white')
outlookLabel.place(x=700, y=390)

teams_logo = PhotoImage(file='teams.png')
teamsLabel = Label(login_window, image=teams_logo, bg='white')
teamsLabel.place(x=800, y=390)

signupLabel = Label(login_window, text="Vous n'avez pas de compte ?", font=('Open Sans', 10, 'bold'), fg='blue4', bg='white')
signupLabel.place(x=610, y=490)

newaccountButton = Button(login_window, text='créer un compte', font=('open Sans', 11, 'bold underline'),
                          fg='white', bg='blue4', activeforeground='white', activebackground='blue4',
                          cursor='hand2', bd=0, command=signup_page)
newaccountButton.place(x=815, y=485)

login_window.mainloop()