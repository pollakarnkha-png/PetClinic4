import json
import os
from datetime import date, datetime
from uuid import uuid4

import pet_manager

MED_FILE = "med_stock.json"
PAYMENT_FILE = "payment_history.json"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_lot(lot):
    if not isinstance(lot, dict):
        return None

    exp_date = str(lot.get("Expiration date", "N/A")).strip()
    qty = _to_int(lot.get("Quantity", 0))

    if qty < 0:
        qty = 0

    return {
        "Expiration date": exp_date if exp_date else "N/A",
        "Quantity": qty
    }


def _recalculate_item(item):
    if not isinstance(item, dict):
        return {}

    lots = item.get("lots", [])
    if not isinstance(lots, list):
        lots = []

    normalized_lots = []
    for lot in lots:
        lot_data = _normalize_lot(lot)
        if lot_data is not None:
            normalized_lots.append(lot_data)

    if not normalized_lots and item.get("Expiration date"):
        dates = item["Expiration date"]
        if isinstance(dates, str):
            dates = [d.strip() for d in dates.split(",") if d.strip()]
        else:
            dates = [str(d).strip() for d in dates if str(d).strip()]

        qty = _to_int(item.get("Quantity", 0))
        if dates:
            share = qty // len(dates)
            extra = qty % len(dates)
            for i, date_value in enumerate(dates):
                q = share + (1 if i < extra else 0)
                normalized_lots.append({
                    "Expiration date": str(date_value),
                    "Quantity": q
                })

    if not normalized_lots:
        normalized_lots.append({
            "Expiration date": "N/A",
            "Quantity": _to_int(item.get("Quantity", 0))
        })

    total_qty = sum(lot["Quantity"] for lot in normalized_lots)
    item["lots"] = normalized_lots
    item["Quantity"] = total_qty
    item["Name"] = str(item.get("Name", "Unknown")).strip() or "Unknown"
    item["Price per unit"] = _to_float(item.get("Price per unit", 0))
    item["Category"] = str(item.get("Category", "general")).strip() or "general"

    return item


def load_stock():
    if not os.path.exists(MED_FILE):
        return {}

    try:
        with open(MED_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

    stock = {}
    for med_id, item in data.items():
        if not isinstance(item, dict):
            continue
        stock[med_id] = _recalculate_item(item)

    return stock


def save_stock(med):
    for item in med.values():
        if isinstance(item, dict):
            _recalculate_item(item)

    with open(MED_FILE, "w", encoding="utf-8") as file:
        json.dump(med, file, ensure_ascii=False, indent=4)


def get_total_stock(item):
    if not isinstance(item, dict):
        return 0
    lots = item.get("lots", [])
    return sum(_to_int(lot.get("Quantity", 0)) for lot in lots if isinstance(lot, dict))


def get_expiry_days(exp_date):
    if not exp_date or exp_date == "N/A":
        return None
    try:
        exp = datetime.strptime(str(exp_date), "%Y-%m-%d").date()
        return (exp - date.today()).days
    except ValueError:
        return None


def get_stock_alerts(med, low_stock_limit=10, expiring_days=30):
    alerts = []

    for med_id, item in med.items():
        total = get_total_stock(item)
        if total <= low_stock_limit:
            alerts.append({
                "type": "low_stock",
                "med_id": med_id,
                "name": item.get("Name", "Unknown"),
                "qty": total
            })

        for lot in item.get("lots", []):
            if not isinstance(lot, dict):
                continue
            days_left = get_expiry_days(lot.get("Expiration date"))
            if days_left is not None and days_left <= expiring_days:
                alerts.append({
                    "type": "expiring_soon",
                    "med_id": med_id,
                    "name": item.get("Name", "Unknown"),
                    "exp_date": lot.get("Expiration date", "N/A"),
                    "qty": _to_int(lot.get("Quantity", 0)),
                    "days_left": days_left
                })

    return alerts


def add_med(med):
    print("\n(------------------ Add New Medicine ------------------)")

    med_id = input("Enter medicine ID: ").strip().upper()
    if not med_id:
        print("Medicine ID cannot be empty!")
        return

    if med_id in med:
        item = med[med_id]
        print(f"{med_id} : {item['Name']} | total stock: {get_total_stock(item)}")

        try:
            qty_add = int(input("Enter the quantity to add to stock: ").strip())
        except ValueError:
            print("Quantity needs to be integer!")
            return

        if qty_add <= 0:
            print("Quantity needs to be more than zero!")
            return

        exp_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
        if not exp_date:
            print("Expiration date cannot be empty!")
            return

        found = False
        for lot in item["lots"]:
            if lot["Expiration date"] == exp_date:
                lot["Quantity"] += qty_add
                found = True
                break

        if not found:
            item["lots"].append({
                "Expiration date": exp_date,
                "Quantity": qty_add
            })

        _recalculate_item(item)
        save_stock(med)
        print("Updated!")
        print(f"{med_id} : {item['Name']} | total stock: {item['Quantity']}")
        return

    name = input("Enter medicine name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return

    try:
        quantity = int(input("Enter initial stock quantity: ").strip())
        price = float(input("Enter price per unit (THB): ").strip())
    except ValueError:
        print("Invalid quantity or price input.\n")
        return

    if quantity <= 0:
        print("Initial stock must be more than zero.")
        return

    exp_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
    if not exp_date:
        print("Expiration date cannot be empty!")
        return

    print("")
    print("(------------------ Category ------------------)")
    print("1.Antimicrobials")
    print("2.Antiparasitics")
    print("3.NSAIDs")
    print("4.CNS")
    print("5.Specific Drugs")
    print("6.General")
    print("")

    choice = input("Choose an option (1-6): ").strip()

    if choice == "1":
        category = "Antimicrobials"
    elif choice == "2":
        category = "Antiparasitics"
    elif choice == "3":
        category = "NSAIDs"
    elif choice == "4":
        category = "CNS"
    elif choice == "5":
        category = "Specific Drugs"
    elif choice == "6":
        category = "General"
    else:
        category = "General"

    print("")
    print("(------------------ Type ------------------)")
    print("1.Rx")
    print("2.OTC")
    print("")
    choice2 = input("Choose an option (1 or 2): ").strip()

    if choice2 == "1":
        type = "Rx"
    elif choice2 == "2":
        type = "OTC"
    else:
        print("Invalid type.")

    med[med_id] = {
        "Name": name,
        "Quantity": quantity,
        "Price per unit": price,
        "Category": category,
        "Type": type,
        "lots": [{
            "Expiration date": exp_date,
            "Quantity": quantity
        }]
    }

    save_stock(med)
    print(f"Added new medicine '{name}' (ID: {med_id}).")


def view_stock(med):
    if not med:
        print("\nStock is currently empty.\n")
        return

    alerts = get_stock_alerts(med)

    print("\n" + "=" * 110)
    print(f"{'Med ID':<8} | {'Name':<25} | {'Qty':<8} | {'Price/Unit':<10} | {'Exp date':<12} | {'Category':<15} | {'Type'}")
    print("-" * 110)

    for med_id, item in med.items():
        name = item.get("Name", "Unknown")
        price = _to_float(item.get("Price per unit", 0))
        category = item.get("Category", "general")
        type = item.get("Type")

        lots = item.get("lots", [])
        if not isinstance(lots, list):
            lots = []

        for idx, lot in enumerate(lots):
            qty = _to_int(lot.get("Quantity", 0))
            exp_date = lot.get("Expiration date", "N/A")
            display_name = name if idx == 0 else ""
            print(
                f"{med_id:<8} | {display_name:<25} | {qty:<8} | "
                f"{price:<10.2f} | {exp_date:<12} | {category:<15} | {type}"
            )

    print("=" * 110)

    print("\nStock alerts:")
    if not alerts:
        print("No warnings.")
    else:
        for alert in alerts:
            if alert["type"] == "low_stock":
                print(f"- LOW STOCK: {alert['med_id']} {alert['name']} -> {alert['qty']} pcs left")
            else:
                print(
                    f"- EXPIRING SOON: {alert['med_id']} {alert['name']} "
                    f"| Exp: {alert['exp_date']} | {alert['days_left']} days left "
                    f"| Qty: {alert['qty']}"
                )

    print()


def get_medicine(med):
    med_name = input("Medicine you want to get: ").strip()

    found = False
    for med_id, item in med.items():
        if item.get("Name", "").lower() == med_name.lower():
            found = True
            lots = sorted(
                item.get("lots", []),
                key=lambda lot: get_expiry_days(lot.get("Expiration date")) if get_expiry_days(lot.get("Expiration date")) is not None else 999999
            )

            if not lots:
                print(f"Medicine '{med_name}' has no stock data.")
                return

            if len(lots) > 1:
                print("Available expiry dates:")
                for i, lot in enumerate(lots, start=1):
                    print(f"{i}. {lot['Expiration date']} -> {lot['Quantity']} pcs")
                try:
                    choice = int(input("Choose expiry date: ").strip())
                except ValueError:
                    print("Invalid choice.")
                    return

                if choice < 1 or choice > len(lots):
                    print("Invalid choice.")
                    return
                selected_lot = lots[choice - 1]
            else:
                selected_lot = lots[0]

            try:
                qty_get = int(input("How many do you want to get: ").strip())
            except ValueError:
                print("Quantity must be integer.")
                return

            if qty_get <= 0:
                print("Quantity need to be more than zero!")
                return

            current = _to_int(selected_lot.get("Quantity", 0))
            if qty_get > current:
                print(f"Not enough stock! Current stock: {current}")
                return

            selected_lot["Quantity"] = current - qty_get

            item["lots"] = [lot for lot in item["lots"] if _to_int(lot.get("Quantity", 0)) > 0]
            _recalculate_item(item)
            save_stock(med)
            print(f"Successfully retrieved {qty_get} of {item['Name']}.")
            return

    if not found:
        print(f"Medicine '{med_name}' not found in stock.")


def edit_stock(med):
    med_id = input("Enter medicine ID: ").strip().upper()
    if med_id not in med:
        print("Invalid ID please try again")
        return

    item = med[med_id]
    print("\n" + "=" * 110)
    print(f"{'Med ID':<8} | {'Name':<25} | {'Qty':<8} | {'Price/Unit':<10} | {'Exp date':<12} | {'Category':<15} | {'Type'}")
    print("-" * 110)

    for idx, lot in enumerate(item.get("lots", [])):
        qty = _to_int(lot.get("Quantity", 0))
        exp_date = lot.get("Expiration date", "N/A")
        name = item.get("Name", "Unknown") if idx == 0 else ""
        print(
            f"{med_id:<8} | {name:<25} | {qty:<8} | "
            f"{float(item.get('Price per unit', 0)):<10.2f} | {exp_date:<12} | {item.get('Category', 'general'):<15} | {item.get('Type')}"
        )

    print("")
    print("Which part do you want to edit?: ")
    print("1.Name")
    print("2.Price per unit")
    print("3.Category")
    print("4.Type")
    print("5.Add stock by expiry date")

    choice = input("Choose an option (1-5): ").strip()

    if choice == "1":
        new_name = input("Edit name to?: ").strip()
        if not new_name:
            print("Name cannot be empty!")
            return
        item["Name"] = new_name

    elif choice == "2":
        try:
            new_price = float(input("Edit price/unit to?: ").strip())
        except ValueError:
            print("Price must be a number.")
            return
        item["Price per unit"] = new_price

    elif choice == "3":
        print("")
        print("(------------------ Category ------------------)")
        print("1.Antimicrobials")
        print("2.Antiparasitics")
        print("3.NSAIDs")
        print("4.CNS")
        print("5.Specific Drugs")
        print("6.General")
        print("")
        
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            new_category = "Antimicrobials"
        elif choice == "2":
            new_category = "Antiparasitics"
        elif choice == "3":
            new_category = "NSAIDs"
        elif choice == "4":
            new_category = "CNS"
        elif choice == "5":
            new_category = "Specific Drugs"
        elif choice == "6":
            new_category = "General"
        else:
            new_category = "General"

        item["Category"] = new_category

    elif choice == "4":
        print("")
        print("(------------------ Type ------------------)")
        print("1.Rx")
        print("2.OTC")
        print("")

        choice2 = input("Choose an option (1 or 2): ").strip()
    
        if choice2 == "1":
            new_type = "Rx"
        elif choice2 == "2":
            new_type = "OTC"
        else:
            print("Invalid type.")

        item["Type"] = new_type

    elif choice == "5":
        exp_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
        if not exp_date:
            print("Expiration date cannot be empty!")
            return
        try:
            qty_add = int(input("Enter quantity to add: ").strip())
        except ValueError:
            print("Quantity must be integer.")
            return

        if qty_add <= 0:
            print("Quantity need to be more than zero!")
            return

        found = False
        for lot in item["lots"]:
            if lot["Expiration date"] == exp_date:
                lot["Quantity"] += qty_add
                found = True
                break

        if not found:
            item["lots"].append({
                "Expiration date": exp_date,
                "Quantity": qty_add
            })

        _recalculate_item(item)
        save_stock(med)
        print(f"Added {qty_add} units to expiry date {exp_date}.")
        return

    _recalculate_item(item)
    save_stock(med)

def load_payment_history():
    if not os.path.exists(PAYMENT_FILE):
        return []

    try:
        with open(PAYMENT_FILE, "r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Unable to read payment history: {error}") from error

    if not isinstance(records, list):
        raise ValueError("Invalid payment history format")
    return records


def save_payment_history(records):
    with open(PAYMENT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)


def view_payment_history():
    try:
        records = load_payment_history()
    except (OSError, ValueError) as error:
        print(f"Unable to read payment history: {error}")
        return

    if not records:
        print("No payment history available.")
        return

    pet_id = input("Enter a pet ID to search, or leave blank to view all: ").strip().upper()
    matching_records = []
    for record in records:
        if not isinstance(record, dict):
            continue
        if not pet_id or str(record.get("pet_id", "")).upper() == pet_id:
            matching_records.append(record)

    if not matching_records:
        print("No payment history found.")
        return

    print("\n(------------------ Payment History ------------------)")
    for record in reversed(matching_records):
        print(
            f"Receipt: {record.get('receipt_id', '-')} | "
            f"Date: {record.get('paid_at', '-')} | "
            f"Pet ID: {record.get('pet_id', '-')} | "
            f"Status: {'Paid' if record.get('status') == 'ชำระแล้ว' else record.get('status', '-')} | "
            f"Total: {_to_float(record.get('total', 0)):.2f} | "
            f"Received by: {record.get('staff', '-')}"
        )


def make_payment(username=""):
    med = load_stock()
    pets = pet_manager.load_pet()
    pet_id = input("Enter pet ID: ").strip().upper()
    pet_info = pets.get(pet_id)
    if not isinstance(pet_info, dict):
        print("Pet ID not found. Payment cancelled.")
        return

    today = date.today()
    date_text = today.isoformat()
    receipt_items = []

    print("\n(------------------ Payment ------------------)")
    print("Enter the medicine name or ID and quantity. Leave blank to finish adding medicines.")
    while True:
        medicine_query = input("Medicine name or ID: ").strip()
        if not medicine_query:
            break

        found = False
        for med_id, item in med.items():
            if (
                med_id.lower() == medicine_query.lower()
                or item.get("Name", "").lower() == medicine_query.lower()
            ):
                found = True
                break

        if not found:
            print("Medicine not found.")
            continue

        try:
            quantity = int(input("Quantity: ").strip())
        except ValueError:
            print("Quantity must be an integer.")
            continue
        if quantity <= 0:
            print("Quantity must be greater than zero.")
            continue

        usable_lots = []
        for lot in item.get("lots", []):
            days_left = get_expiry_days(lot.get("Expiration date"))
            if days_left is not None and days_left >= 0 and _to_int(lot.get("Quantity", 0)) > 0:
                usable_lots.append(lot)
        usable_lots.sort(key=lambda lot: lot.get("Expiration date", ""))

        available = 0
        for lot in usable_lots:
            available += _to_int(lot.get("Quantity", 0))

        if quantity > available:
            print(f"Insufficient unexpired stock. Available: {available}")
            continue

        remaining = quantity
        for lot in usable_lots:
            taken = min(remaining, _to_int(lot.get("Quantity", 0)))
            lot["Quantity"] -= taken
            remaining -= taken
            if remaining == 0:
                break

        unit_price = _to_float(item.get("Price per unit", 0))
        receipt_items.append({
            "description": f"{item.get('Name', 'ไม่ทราบ')} ({med_id}) x {quantity}",
            "amount": quantity * unit_price
        })
        item["lots"] = [lot for lot in item.get("lots", []) if _to_int(lot.get("Quantity", 0)) > 0]
        _recalculate_item(item)

    print("Enter the medical equipment name and price. Leave the name blank to finish.")
    while True:
        equipment = input("Equipment: ").strip()
        if not equipment:
            break
        try:
            price = float(input("Price: ").strip())
        except ValueError:
            print("Price must be a number.")
            continue
        if price < 0:
            print("Price cannot be negative.")
            continue
        receipt_items.append({"description": equipment, "amount": price})

    try:
        treatment_fee = float(input("Treatment fee (enter 0 if none): ").strip() or "0")
    except ValueError:
        print("Treatment fee must be a number.")
        return
    if treatment_fee < 0:
        print("Treatment fee cannot be negative.")
        return
    if treatment_fee:
        receipt_items.append({"description": "ค่ารักษา", "amount": treatment_fee})

    total = 0
    for entry in receipt_items:
        total += entry["amount"]

    print("\n(------------------ Payment Summary ------------------)")
    for entry in receipt_items:
        description = entry["description"].replace("ไม่ทราบ", "Unknown").replace("ค่ารักษา", "Treatment fee")
        print(f"{description}: {entry['amount']:.2f}")
    print(f"Total due: {total:.2f}")

    if input("Confirm that full payment has been received? (enter y to confirm): ").strip().lower() != "y":
        print("Payment was not confirmed; stock was not saved and no receipt was issued.")
        return

    username = str(username).strip() or "Unknown"
    receipt_id = f"PAY-{today.strftime('%Y%m%d')}-{uuid4().hex[:12].upper()}"
    paid_at = datetime.now().isoformat(timespec="seconds")

    try:
        payment_records = load_payment_history()
    except (OSError, ValueError) as error:
        print(f"Unable to save payment: {error}")
        return

    payment_records.append({
        "receipt_id": receipt_id,
        "paid_at": paid_at,
        "pet_id": pet_id,
        "pet_name": pet_info.get("Name", "-"),
        "owner": pet_info.get("Owner", "-"),
        "staff": username,
        "status": "ชำระแล้ว",
        "total": total,
        "items": receipt_items
    })

    try:
        save_payment_history(payment_records)
    except OSError as error:
        print(f"Unable to save payment history: {error}")
        return

    try:
        save_stock(med)
    except OSError as error:
        payment_records.pop()
        try:
            save_payment_history(payment_records)
        except OSError as rollback_error:
            print(
                f"Failed to save stock ({error}) and could not remove the saved payment record "
                f"({rollback_error})"
            )
            return
        print(f"Failed to save stock, so the payment was cancelled: {error}")
        return

    print("\n(============= RECEIPT =============)")
    print(f"Receipt number: {receipt_id}")
    print(f"Date: {date_text}")
    print(f"Pet ID: {pet_id}")
    print(f"Pet name: {pet_info.get('Name', '-')}")
    print(f"Owner: {pet_info.get('Owner', '-')}")
    for entry in receipt_items:
        description = entry["description"].replace("ไม่ทราบ", "Unknown").replace("ค่ารักษา", "Treatment fee")
        print(f"{description}: {entry['amount']:.2f}")
    print(f"Total: {total:.2f}")
    print("Payment status: Paid")
    print(f"Dispensed by: {username}")
    print("=============================")
    