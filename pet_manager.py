import json
import os
import textwrap

DATA_FILE = "pet_database.json"

def load_pet():
    """Loads the user database from a JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_pet(pet):
    """Saves the user database to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(pet, file, indent=4)

def runnum(pet):
    if not isinstance(pet, dict):
        return "00001"
    next_no = len(pet) + 1
    return f"{next_no:05d}"

def register(pet):
    """New pet registration."""
    print("\n(------------------ Registration ------------------)")
    pet = load_pet()

    petname = input("Enter pet name : ").strip()
    if not petname:
      print("Name cannot be empty!")
      return
    
    species = input("Enter pet species : ").strip()
    if not species:
      print("Name cannot be empty!")
      return

    breed = input("Enter pet breed : ").strip()
    if not breed:
      breed = "-"

    gender = input("Gender (m/f) : ").strip()
    if not gender:
      gender = "N/A"

    ageY = int(input("Age (Year) : "))
    if not ageY:
      ageY = "-"

    ageM = int(input("Age (month) : "))
    if not ageM:
      ageM = "-"

    blood = input("Blood type : ").strip()
    if not blood:
      blood = "-"

    weight = float(input("Weight : "))
    if not weight:
      weight = "-"

    identity = input("Enter pet's identity : ").strip()
    if not identity:
      identity = "-"

    all = input("Enter any drug allergy or other allergy : ").strip()
    if not all:
      all = "-"

    med_his = "-"
    when = "-"

    owner = input("Enter owner name : ").strip()
    if not owner:
      print("Name cannot be empty!")
      return

    contact = input("Enter owner contact : ").strip()
    if not contact:
      print("Contact cannot be empty!")
      return

    s_code = species[0].upper()
    b_code = breed[0].upper() if breed != "-" else "X"
    pet_id = f"{s_code}{b_code}{runnum(pet)}"

    pet[pet_id] = {
            "Name": petname,
            "Species": species,
            "Breed": breed,
            "Gender": gender,
            "Age": f"{ageY} Year {ageM} Month",
            "Blood Type": blood,
            "Weight": weight,
            "Identity": identity,
            "Allergic React": all,
            "Owner": owner,
            "Contact": contact,
            "Medical History": [{
                "Medical History": med_his,
                "When": when
            }]
        }

    save_pet(pet)
    print(f"{petname} own by {owner}. ID : {pet_id}")

def search_pet(pet):
   pet = load_pet()
   pet_id = input("Enter pet ID : ").strip()

   if not pet_id:
      print("Not found")
      return

   if pet_id in pet:
      print("\n" + "=" * 180)
      print(f"{'ID':<8} | {'Name':<8} | {'Species':<8} | {'Breed':<20} | {'Gender':<8} | {'Blood Type':<10} | {'Weight':<10} | {'Identity':<30} | {'Allergic React':<25} | {'Owner':<25} | {'Contact':<25}")
      print("-" * 180)

      petname = pet[pet_id]["Name"]
      species = pet[pet_id]["Species"]
      breed = pet[pet_id]["Breed"]
      gender = pet[pet_id]["Gender"]
      blood = pet[pet_id]["Blood Type"]
      weight = pet[pet_id]["Weight"]
      identity = str(pet[pet_id]["Identity"])
      all = pet[pet_id]["Allergic React"]
      owner = pet[pet_id]["Owner"]
      contact = pet[pet_id]["Contact"]

      identity_lines = textwrap.wrap(identity, width=30) or [""]

      print(
          f"{pet_id:<8} | {petname:<8} | {species:<8} | {breed:<20} | {gender:<8} | {blood:<10} | {weight:<10} | {identity_lines[0]:<30} | {all:<25} | {owner:<25} | {contact:<25}"
      )
      for line in identity_lines[1:]:
          print(
              f"{'':<8} | {'':<8} | {'':<8} | {'':<20} | {'':<8} | {'':<10} | {'':<10} | {line:<30} | {'':<25} | {'':<25} | {'':<25}"
          )

def pet_search(pet):
  pet = load_pet()
  search_name = input("Enter pet name : ").strip()
  owner = input("Enter owner name : ").strip()
  for pet_id, pet_data in pet.items():
      if search_name == pet_data["Name"] and owner == pet_data["Owner"]:
          print("\n" + "=" * 200)
          print(f"{'ID':<8} | {'Name':<8} | {'Species':<8} | {'Breed':<20} | {'Gender':<8} | {'Blood Type':<10} | {'Weight':<10} | {'Identity':<30} | {'Allergic React':<25} | {'Owner':<25} | {'Contact':<25}")
          print("-" * 200)
      
          petname = pet[pet_id]["Name"]
          species = pet[pet_id]["Species"]
          breed = pet[pet_id]["Breed"]
          gender = pet[pet_id]["Gender"]
          blood = pet[pet_id]["Blood Type"]
          weight = pet[pet_id]["Weight"]
          identity = str(pet[pet_id]["Identity"])
          all = pet[pet_id]["Allergic React"]
          owner = pet[pet_id]["Owner"]
          contact = pet[pet_id]["Contact"]
      
          identity_lines = textwrap.wrap(identity, width=40) or [""]
      
          print(
              f"{pet_id:<8} | {petname:<8} | {species:<8} | {breed:<20} | {gender:<8} | {blood:<10} | {weight:<10} | {identity_lines[0]:<30} | {all:<25} | {owner:<25} | {contact:<25}"
          )
          for line in identity_lines[1:]:
              print(
                  f"{'':<8} | {'':<8} | {'':<8} | {'':<20} | {'':<8} | {'':<10} | {'':<10} | {line:<30} | {'':<25} | {'':<25} | {'':<25}"
              )
          return pet_id
  print("Pet not found.")
  if input("Do you want to register a new pet? (y/n): ").strip().lower() == "y":
      register(pet)
  else:
      print("Returning to the Pet Manager.")