# Handle login and verify permissions (admin/doctor/staff).

import hashlib
import json
import os
import Panel

# File where user database will be saved
DATA_FILE = "user_database.json"
ROLE_FILE = "user_role.json"

def load_users():
    """Loads the user database from a JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def load_roles():
    """Loads the user roles from a JSON file."""
    if not os.path.exists(ROLE_FILE):
        return {}
    with open(ROLE_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    """Saves the user database to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

def hash_password(password):
    """Securely hashes a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register():
    """Handles new user registration."""
    print("\n(------------------ Registration ------------------)")
    users = load_users()
    
    username = input("Enter a new username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return

    if username in users:
        print("Username already exists! Try logging in.")
        return

    password = input("Enter a secure password: ")
    if len(password) < 6:
        print("Password must be at least 6 characters long.")
        return

    # Store the username and the hashed version of the password
    users[username] = hash_password(password)
    save_users(users)
    print(f"User '{username}' registered successfully!")

def login():
    """Handles user login authentication."""
    print("\n(------------------ Login ------------------)")
    users = load_users()
    role = load_roles()
    
    username = input("Username: ").strip()
    password = input("Password: ")

    hashed_input_password = hash_password(password)

    if username in users and users[username] == hashed_input_password:
        user_role = role.get(username)
        if user_role == "admin":
            print("Welcome, Admin! You have full access.")
            Panel.adminPanel(username)
        elif user_role == "doctor":
            print("Welcome, Doctor! You have access to medical records.")
            Panel.doctorPanel(username)
        elif user_role == "staff":
            print("Welcome, Staff! You have access to general operations.")
            Panel.staffPanel(username)
        else:
            print(f"Your account '{username}' has no assigned role. Contact an administrator.")
        return True
    else:
        print("Invalid username or password.")
        return False

# Maybe the return value can be used for additional processing.

def SetRole():
    """Sets the role for a user."""
    print("\n(------------------ Set Role ------------------)")
    users = load_users()
    roles = load_roles()
    
    username = input("Enter the username to set role: ").strip()
    if username not in users:
        print("Username does not exist! Please register first.")
        return

    print("Available roles: admin, doctor, staff")
    new_role = input("Enter the new role for the user: ").strip().lower()

    if new_role not in ["admin", "doctor", "staff"]:
        print("Invalid role! Please choose from admin, doctor, or staff.")
        return

    roles[username] = new_role
    with open(ROLE_FILE, "w") as file:
        json.dump(roles, file, indent=4)
    
    print(f"Role for user '{username}' has been set to '{new_role}'.")

def RemoveRole():
    """Removes the role for a user."""
    print("\n(------------------ Remove Role ------------------)")
    roles = load_roles()
    
    username = input("Enter the username to remove role: ").strip()
    if username not in roles:
        print("Username does not have a role assigned.")
        return

    del roles[username]
    with open(ROLE_FILE, "w") as file:
        json.dump(roles, file, indent=4)
    
    print(f"Role for user '{username}' has been removed.")
    