# Treatment functions (record symptoms, view history, and issue prescriptions).
import datetime
import inventory
import pet_manager


def treatment_record(username=""):
    """Record a SOAP treatment visit, dispense medication, and print a receipt."""
    pet = pet_manager.load_pet()
    pet_id = input("Enter pet ID: ").strip()

    if pet_id not in pet:
        print("Pet not found!")
        return
    pet_info = pet[pet_id]
    print(f"Name: {pet_info['Name']}")
    print(f"Species: {pet_info['Species']}")
    print(f"Breed: {pet_info['Breed']}")
    print(f"Gender: {pet_info['Gender']}")
    print(f"Age: {pet_info['Age']}")
    print(f"Blood Type: {pet_info['Blood Type']}")
    print(f"Weight: {pet_info['Weight']}")
    print(f"Identity: {pet_info['Identity']}")
    print(f"Allergic Reaction: {pet_info['Allergic React']}")
    print(f"Owner: {pet_info['Owner']}")
    print(f"Contact: {pet_info['Contact']}")
    
    print("(------------------ Treatment History ------------------)")
    history = pet_info.get("Treatment History", [])
    if not isinstance(history, list):
        history = []

    print("(------------------ Treatment Record ------------------)")
    while True:
        choice = input("Select 1. New treatment  2. Continuing treatment: ").strip()
        if choice in ("1", "2"):
            break
        print("Please select 1 or 2.")

    if choice == "2":
        if not history:
            print("No previous treatment history found. Starting a new treatment record.")
            choice = "1"
        else:
            last_completed = -1
            for index, old_record in enumerate(history):
                if isinstance(old_record, dict) and old_record.get("Treatment Status") == "Completed":
                    last_completed = index

            ongoing_history = []
            for index, old_record in enumerate(history):
                if index > last_completed and isinstance(old_record, dict):
                    if old_record.get("Treatment Status") != "Ongoing":
                        continue
                    ongoing_history.append(old_record)
            if ongoing_history:
                print("(------------------ Ongoing Treatment History ------------------)")
            else:
                print("No ongoing treatment history found.")
            for old_record in ongoing_history:
                print(f"Date: {old_record.get('Date', '-')}")
                print(f"Assessment: {old_record.get('Assessment', '-')}")
                print(f"Plan: {old_record.get('Plan', '-')}\n")

    today = datetime.date.today().isoformat()
    weight = pet_info.get("Weight", "")
    subjective = input("S — Subjective information (symptoms/history reported by the owner): ").strip()
    temperature = input("O — Body temperature (°C): ").strip()
    heart_rate = input("O — Heart rate (beats/min; include rhythm or murmur): ").strip()
    respiratory_rate = input("O — Respiratory rate (breaths/min; include breathing pattern): ").strip()
    other_exam = []
    print("O — Other examination findings (specify finding and result; leave blank to finish)")
    while True:
        exam_item = input("Finding and result: ").strip()
        if not exam_item:
            break
        other_exam.append(exam_item)
    assessment = input("A — Assessment/diagnosis/differential diagnosis: ").strip()
    plan = input("P — Treatment plan/medication/procedure/advice: ").strip()

    stock = inventory.load_stock()
    medicines = []
    medication_total = 0.0
    if stock:
        print("(------------------ Dispense Medication (enter a medicine name or ID; leave blank to finish) ------------------)")
        while True:
            medicine_query = input("Medicine name or ID: ").strip()
            if not medicine_query:
                break
            match_code = ""
            match_item = None
            for code, item in stock.items():
                if medicine_query.lower() == str(code).lower():
                    match_code = code
                    match_item = item
                    break
                if medicine_query.lower() == str(item.get("Name", "")).lower():
                    match_code = code
                    match_item = item
                    break
            if match_item is None:
                print("Medicine name or ID not found in med_stock.")
                continue
            try:
                quantity = float(input("Medicine quantity: ").strip())
                price = float(match_item.get("Price per unit", 0))
                available = inventory.get_total_stock(match_item)
                if quantity <= 0 or quantity > available or price < 0:
                    print("Quantity must be greater than 0 and no more than the available stock; price cannot be negative.")
                    continue
            except (ValueError, TypeError):
                print("Invalid medicine quantity, stock, or price.")
                continue
            medicine_name = match_item.get("Name", match_code)
            medicines.append({
                "Code": match_code,
                "Name": medicine_name,
                "Quantity": quantity,
                "Unit Price": price,
                "Total": quantity * price
            })
            medication_total += quantity * price
    else:
        print("No usable medicine data found in med_stock.")

    supplies = []
    while True:
        supply_name = input("Medical equipment name (leave blank to finish): ").strip()
        if not supply_name:
            break
        while True:
            try:
                supply_price = float(input("Equipment price: ").strip() or "0")
                if supply_price < 0:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a valid, non-negative amount.")
        supplies.append({"Name": supply_name, "Price": supply_price})
    while True:
        try:
            treatment_fee = float(input("Treatment fee: ").strip() or "0")
            if treatment_fee < 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid, non-negative amount.")
    while True:
        status_choice = input("Treatment status 1. Ongoing  2. Completed: ").strip()
        if status_choice in ("1", "2"):
            break
        print("Please select 1 or 2.")
    next_recheck = ""
    if status_choice == "1":
        while not next_recheck:
            next_recheck = input("Next recheck date (YYYY-MM-DD): ").strip()

    prior_dates = []
    if choice == "2":
        for old_record in history:
            if isinstance(old_record, dict) and old_record.get("Date"):
                prior_dates.append(old_record.get("Date"))
    start_date = today
    for prior_date in prior_dates:
        if prior_date < start_date:
            start_date = prior_date
    treatment_status = "Completed"
    if status_choice == "1":
        treatment_status = "Ongoing"

    record = {
        "Date": today,
        "S": subjective,
        "O": {
            "Weight (kg)": weight,
            "Temperature (°C)": temperature,
            "Heart Rate (bpm)": heart_rate,
            "Respiratory Rate (breaths/min)": respiratory_rate,
            "Other Examination": other_exam
        },
        "Assessment": assessment,
        "Plan": plan,
        "Doctor": username or "ไม่ระบุ",
        "Medicines": medicines,
        "Medical Equipment": supplies,
        "Treatment Fee": treatment_fee,
        "Treatment Status": treatment_status,
        "Treatment Start Date": start_date,
        "Next Recheck Date": next_recheck or None,
    }
    history.append(record)
    pet_info["Treatment History"] = history
    if status_choice == "2":
        pet_info["Treatment Status"] = "Completed"
        pet_info["Treatment End Date"] = today
    else:
        pet_info["Treatment Status"] = "Ongoing"
        pet_info["Treatment Start Date"] = start_date
        pet_info["Next Recheck Date"] = next_recheck
    pet_manager.save_pet(pet)

    print("\nTreatment record saved:")
    print(f"Date: {today}\nS — Reported information: {subjective}")
    print(f"O — Weight: {weight} kg | Temperature: {temperature} °C | HR: {heart_rate} | RR: {respiratory_rate}")
    exam_summary = "-"
    if other_exam:
        exam_summary = "; ".join(other_exam)
    print(f"  — Other examination findings: {exam_summary}")
    print(f"A — Assessment: {assessment}\nP — Treatment plan: {plan}")
    print(f"Attending doctor: {username or 'Not specified'}")
    if status_choice == "1":
        print(f"Treatment Status: Ongoing | Start: {start_date} | Latest: {today} | Next appointment: {next_recheck}")
    else:
        treatment_dates = []
        for date in prior_dates + [today]:
            if date not in treatment_dates:
                treatment_dates.append(date)
        treatment_dates.sort()
        print(
            f"Treatment Status: Completed | Start: {start_date} | "
            f"Treatment dates: {', '.join(treatment_dates)} | End date: {today}"
        )
    if input("Print the treatment results and next appointment? (y/n): ").strip().lower() == "y":
        print("\n(------------------ Treatment Results and Appointment ------------------)")
        print(f"Pet name: {pet_info.get('Name', '-')}")
        print(f"Owner name: {pet_info.get('Owner', '-')}")
        print(f"Attending doctor: {username or 'Not specified'}")
        print(f"Treatment result: {assessment}")
        print(f"Treatment plan: {plan}")
        print(f"Next appointment: {next_recheck or '-'}")

    equipment_total = 0
    for item in supplies:
        equipment_total += item["Price"]
    total = medication_total + equipment_total + treatment_fee
    print("\n(------------------ Prescription ------------------)")
    print(f"Prescribing doctor: {username or 'Not specified'}")
    for item in medicines:
        print(f"Medicine: {item['Name']} | Quantity: {item['Quantity']:g} | Price: {item['Total']:.2f}")
    for item in supplies:
        print(f"Medical equipment: {item['Name']} | Price: {item['Price']:.2f}")
    print(f"Treatment fee: {treatment_fee:.2f}")
    print(f"Total (medicine + equipment + treatment): {total:.2f}")
    print("Please present the prescription at the pharmacy to collect the medicine.")
    if input("Print the prescription? (y/n): ").strip().lower() == "y":
        print("Prescription printed successfully.")


def treatment_history():
    """Search for an animal by name or ID and display treatment history by episode."""
    pets = pet_manager.load_pet()
    search = input("Search for an animal by name or ID: ").strip().lower()
    matches = []
    for pet_id, info in pets.items():
        if search in str(pet_id).lower() or search in str(info.get("Name", "")).lower():
            matches.append((pet_id, info))

    if not matches:
        print("No animal found matching that name or ID.")
        return
    if len(matches) > 1:
        print("Multiple animals found:")
        for pet_id, info in matches:
            print(f"ID: {pet_id} | Name: {info.get('Name', '-')}")
        selected_id = input("Enter the ID of the animal to view: ").strip()
        selected_pet = None
        for pet_id, info in matches:
            if pet_id == selected_id:
                selected_pet = (pet_id, info)
                break
        if not selected_pet:
            print("Selected ID not found.")
            return
        pet_id = selected_pet[0]
        pet_info = selected_pet[1]
    else:
        pet_id = matches[0][0]
        pet_info = matches[0][1]

    print("\n(------------------ Pet Information ------------------)")
    print(f"ID: {pet_id}")
    print(f"Name: {pet_info['Name']}")
    print(f"Species: {pet_info['Species']}")
    print(f"Breed: {pet_info['Breed']}")
    print(f"Gender: {pet_info['Gender']}")
    print(f"Age: {pet_info['Age']}")
    print(f"Blood Type: {pet_info['Blood Type']}")
    print(f"Weight: {pet_info['Weight']}")
    print(f"Identity: {pet_info['Identity']}")
    print(f"Allergic Reaction: {pet_info['Allergic React']}")
    print(f"Owner: {pet_info['Owner']}")
    print(f"Contact: {pet_info['Contact']}")

    print("\n(------------------ Treatment Information and History ------------------)")
    history = pet_info.get("Treatment History", [])
    if not isinstance(history, list) or not history:
        print("No treatment history found.")
        return

    episodes = {}
    for record in history:
        if not isinstance(record, dict):
            continue
        record_date = record.get("Date")
        if record_date:
            record_date = str(record_date)
        else:
            record_date = "Date not specified"
        start_date = record.get("Treatment Start Date")
        if not start_date:
            start_date = record.get("Start Date")
        if not start_date:
            start_date = record_date
        start_date = str(start_date)
        if start_date not in episodes:
            episodes[start_date] = []
        episodes[start_date].append(record)

    for start_date in sorted(episodes):
        records = episodes[start_date]
        records.sort(key=lambda item: str(item.get("Date") or ""))
        dates = []
        completed = False
        for record in records:
            if record.get("Date"):
                dates.append(str(record.get("Date")))
            status = str(record.get("Treatment Status", record.get("Status", ""))).lower()
            if status in ("completed", "สำเร็จการรักษา"):
                completed = True

        end_date = "Date not specified"
        if dates:
            end_date = dates[-1]
        episode_status = "Ongoing"
        if completed:
            episode_status = "Completed"
        print(f"\n(------------------ {episode_status} ------------------)")
        print(f"Treatment start date: {start_date}")
        if completed:
            print(f"Treatment completion date: {end_date}")
        else:
            date_summary = "-"
            if dates:
                date_summary = ", ".join(dates)
            print(f"Treatment dates to date: {date_summary}")

        for record in records:
            treatment_date = record.get("Date", "-")
            print(f"\n(------------------ Treatment date: {treatment_date} ------------------)")
            doctor = record.get("Doctor", "Not specified")
            if doctor == "ไม่ระบุ":
                doctor = "Not specified"
            print(f"Attending doctor: {doctor}")
            print(f"S — Reported information: {record.get('S', record.get('Subjective', '-'))}")
            objective = record.get("O", record.get("Objective", {}))
            if not isinstance(objective, dict):
                objective = {}
            print("O — Examination findings:")
            if objective:
                for key, value in objective.items():
                    if isinstance(value, (list, tuple)):
                        value = "; ".join(str(item) for item in value) or "-"
                    if value is None or value == "":
                        value = "-"
                    print(f"  - {key}: {value}")
            else:
                print("  - No data")
            print(f"A — Assessment: {record.get('Assessment', '-')}")
            print(f"P — Treatment plan: {record.get('Plan', '-')}")
            status = record.get("Treatment Status", record.get("Status"))
            if status:
                if status == "รักษาต่อเนื่อง":
                    display_status = "Ongoing"
                elif status == "สำเร็จการรักษา":
                    display_status = "Completed"
                else:
                    display_status = status
                print(f"Treatment status: {display_status}")

            medicines = record.get("Medicines", [])
            equipment = record.get("Medical Equipment", [])
            medicine_total = 0.0
            equipment_total = 0.0
            print("Medicines:")
            if isinstance(medicines, list):
                for medicine in medicines:
                    if not isinstance(medicine, dict):
                        print(f"  - {medicine}")
                        continue
                    amount = medicine.get("Total", 0) or 0
                    medicine_total += amount
                    print(
                        f"  - {medicine.get('Name', '-')} | "
                        f"Quantity: {medicine.get('Quantity', '-')} | Price: {amount:.2f}"
                    )
            if not medicines:
                print("  - None")
            print("Medical equipment:")
            if isinstance(equipment, list):
                for item in equipment:
                    if not isinstance(item, dict):
                        print(f"  - {item}")
                        continue
                    price = item.get("Price", 0) or 0
                    equipment_total += price
                    print(f"  - {item.get('Name', '-')} | Price: {price:.2f}")
            if not equipment:
                print("  - None")
            treatment_fee = record.get("Treatment Fee", 0) or 0
            print(f"Treatment fee: {treatment_fee:.2f}")
            print(f"Total cost: {medicine_total + equipment_total + treatment_fee:.2f}")
            next_recheck = record.get("Next Recheck Date", record.get("Next Appointment"))
            if next_recheck:
                print(f"Next recheck date: {next_recheck}")

        if not completed:
            next_recheck = "-"
            for record in reversed(records):
                next_recheck = record.get("Next Recheck Date", record.get("Next Appointment"))
                if next_recheck:
                    break
            if not next_recheck:
                next_recheck = "-"
            if next_recheck != "-":
                print(f"Next appointment for this treatment episode: {next_recheck}")