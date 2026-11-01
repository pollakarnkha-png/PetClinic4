import auth
import inventory
import pet_manager
import queue_sys
import textwrap
import treatment
import json


def adminPanel(username=""):
    """Admin access only"""
    while True:
        print("\n(============= MAIN MENU =============)")
        print("1.Set roles")
        print("2.Remove role")
        print("3.Stock manager")
        print("4.Pet Manager")
        print("5.Prescribe medicine")
        print("6.Treatment menu")
        print("7.Queue System")
        print("8.Make payment")
        print("9.Payment history")
        print("10.Logout")

        choice = input("Choose an option (1-10): ").strip()

        if choice == "1":
            auth.SetRole()
        elif choice == "2":
            auth.RemoveRole()
        elif choice == "3":
            while True:
                print("\n(------------------ Stock Manager ------------------)")
                print("1.Add/Update stock")
                print("2.View stock")
                print("3.Edit stock detail")
                print("4.Exit")

                choice = input("Choose an option (1-4): ").strip()
                med = inventory.load_stock()

                if choice == "1":
                    inventory.add_med(med)
                elif choice == "2":
                    inventory.view_stock(med)
                    input("Enter any key to exit: ")
                elif choice == "3":
                    inventory.edit_stock(med)
                elif choice == "4":
                    break
        elif choice == "4":
            while True:
                print("\n(------------------ Pet Manager ------------------)")
                print("1.Pet registeration")
                print("2.Search pet")
                print("3.Exit")

                choice = input("Choose an option (1-3): ").strip()
                pet = pet_manager.load_pet()

                if choice == "1":
                    pet = pet_manager.load_pet()
                    pet_manager.register(pet)
                elif choice == "2":
                    pet_manager.pet_search(pet)
                elif choice == "3":
                    break
        elif choice == "5":
            med = inventory.load_stock()
            inventory.get_medicine(med)
        elif choice == "6":
            while True:
                print("\n(------------------ Treatment Menu ------------------)")
                print("1. Record Treatment")
                print("2. Treatment History")
                print("3.Exit")

                choice = input("Choose an option (1-3): ").strip()

                if choice == "1":
                    treatment.treatment_record(username)
                elif choice == "2":
                    treatment.treatment_history()
                elif choice == "3":
                    break
        elif choice == "7":
            print("\n(------------------ Queue System ------------------)")
            while True:
                print("1.Add queue")
                print("2.Call queue")
                print("3.View queue")
                print("4.View queue status")
                print("5.Reset queue")
                print("6.Exit")

                choice = input("Choose an option (1-6): ").strip()

                if choice == "1":
                    pet_id = input("Enter pet ID : ").strip().upper()
                    if not pet_id:
                        pet = pet_manager.load_pet()
                        print("")
                        pet_manager.pet_search(pet)
                    queue_sys.add_queue(pet_id)
                elif choice == "2":
                    queue_sys.call_queue()
                elif choice == "3":
                    queue_sys.view_queue()
                elif choice == "4":
                    queue_sys.queue_status()
                elif choice == "5":
                    queue_sys.reset_queue()
                elif choice == "6":
                    break
        elif choice == "8":
            inventory.make_payment(username)
        elif choice == "9":
            inventory.view_payment_history()
        elif choice == "10":
            print("Logging out...")
            break


def doctorPanel(username=""):
    """Doctor access only"""
    while True:
        print("\n(============= DOCTOR PANEL =============)")
        print("1.Treatment menu")
        print("2.Call queue")
        print("3.View queue status")
        print("4.Logout")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            while True:
                print("\n(------------------ Treatment Menu ------------------)")
                print("1. Record Treatment")
                print("2. Treatment History")
                print("3.Exit")

                choice = input("Choose an option (1-3): ").strip()

                if choice == "1":
                    treatment.treatment_record(username)
                elif choice == "2":
                    treatment.treatment_history()
                elif choice == "3":
                    break
        elif choice == "2":
            print("\n(------------------ Call Queue ------------------)")
            queue_sys.call_queue()
        elif choice == "3":
            print("\n(------------------ Queue Status ------------------)")
            queue_sys.queue_status()
        elif choice == "4":
            print("Logging out...")
            break

def staffPanel(username=""):
    """Staff access only"""
    while True:
        print("\n(============= STAFF PANEL =============)")
        print("1.Pet Manager")
        print("2.Queue System")
        print("3.Make payment")
        print("4.Payment history")
        print("5.Logout")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            while True:
                print("\n(------------------ Pet Manager ------------------)")
                print("1.Pet registeration")
                print("2.Search pet")
                print("3.Exit")

                choice = input("Choose an option (1-3): ").strip()
                pet = pet_manager.load_pet()

                if choice == "1":
                    pet = pet_manager.load_pet()
                    pet_manager.register(pet)
                elif choice == "2":
                    pet_manager.pet_search(pet)
                elif choice == "3":
                    break

        elif choice == "2":
            while True:
                print("\n(------------------ Queue System ------------------)")
                print("1.Add queue")
                print("2.Call queue")
                print("3.View queue")
                print("4.View queue status")
                print("5.Reset queue")
                print("6.Exit")

                choice = input("Choose an option (1-6): ").strip()

                if choice == "1":
                    pet_id = input("Enter pet ID : ").strip().upper()
                    if not pet_id:
                        pet = pet_manager.load_pet()
                        print("")
                        pet_manager.pet_search(pet)
                    queue_sys.add_queue(pet_id)
                elif choice == "2":
                    queue_sys.call_queue()
                elif choice == "3":
                    queue_sys.view_queue()
                elif choice == "4":
                    queue_sys.queue_status()
                elif choice == "5":
                    queue_sys.reset_queue()
                elif choice == "6":
                    break
                
        elif choice == "3":
            inventory.make_payment(username)
        elif choice == "4":
            inventory.view_payment_history()
        elif choice == "5":
            break
