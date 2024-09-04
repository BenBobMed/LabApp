from tkinter import *
import subprocess

def open_materiel():
    # Lancer le fichier materiel.py
    subprocess.Popen(["python", "materiel.py"])

def open_laboratoire():
    # Lancer le fichier user.py
    subprocess.Popen(["python", "user.py"])

# Créer la fenêtre principale
main_window = Tk()
main_window.title("Choix de réservation")
main_window.geometry("1000x1000")

# Ajouter des boutons pour chaque option de réservation
Label(main_window, text="Choisissez une option de réservation", font=("Helvetica", 14)).pack(pady=20)

materiel_button = Button(main_window, text="Réservation de matériel", command=open_materiel, width=30)
materiel_button.pack(pady=10)

laboratoire_button = Button(main_window, text="Réservation de laboratoire", command=open_laboratoire, width=30)
laboratoire_button.pack(pady=10)

# Lancer la fenêtre principale
main_window.mainloop()
