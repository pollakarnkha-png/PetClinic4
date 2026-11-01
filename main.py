# Main program file (displays the menu and calls other modules).

import auth

def main():
    """Main program menu loop."""
    while True:
        print("\n(============= MAIN MENU =============)")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Choose2 an option (1-3): ").strip()
        
        if choice == "1":
            auth.register()
        elif choice == "2":
            auth.login()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()