# Test.py
import globals

def print_authenticated_info():
    if globals.authenticated_email is not None and globals.authenticated_id is not None:
        print(f"Authenticated Email: {globals.authenticated_email}")
        print(f"Authenticated ID: {globals.authenticated_id}")
    else:
        print("Global variables are not set or still at default.")
