import os
import json
import re

# =========================
# Globals
# =========================
contacts_file = "contacts.json"
contacts = {}

# =========================
# Helper Functions
# =========================
def load_contacts():
    global contacts
    if os.path.exists(contacts_file):
        with open(contacts_file, "r", encoding="utf-8") as f:
            contacts = json.load(f)
    else:
        contacts = {}

def save_contacts():
    with open(contacts_file, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4)

def display_contacts(filter_term=None):
    if not contacts:
        print("\nNo contacts available.\n")
        return
    
    print("\nContacts List:")
    print("-" * 40)
    for name, info in contacts.items():
        if filter_term and filter_term.lower() not in name.lower():
            continue
        print(f"Name: {name}")
        print(f"  Phone: {info.get('phone', 'N/A')}")
        print(f"  Email: {info.get('email', 'N/A')}")
        print("-" * 40)
    print()

def add_contact():
    name = input("Enter name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return
    phone = input("Enter phone: ").strip()
    email = input("Enter email: ").strip()
    
    contacts[name] = {"phone": phone, "email": email}
    save_contacts()
    print(f"Contact '{name}' added successfully.\n")

def update_contact():
    name = input("Enter the name of the contact to update: ").strip()
    if name not in contacts:
        print(f"No contact found with name '{name}'\n")
        return
    
    print("Leave blank to keep current value.")
    phone = input(f"Enter new phone [{contacts[name].get('phone','')}]: ").strip()
    email = input(f"Enter new email [{contacts[name].get('email','')}]: ").strip()
    
    if phone:
        contacts[name]['phone'] = phone
    if email:
        contacts[name]['email'] = email
    
    save_contacts()
    print(f"Contact '{name}' updated successfully.\n")

def delete_contact():
    name = input("Enter the name of the contact to delete: ").strip()
    if name not in contacts:
        print(f"No contact found with name '{name}'\n")
        return
    confirm = input(f"Are you sure you want to delete '{name}'? (y/n): ").strip().lower()
    if confirm == 'y':
        contacts.pop(name)
        save_contacts()
        print(f"Contact '{name}' deleted.\n")
    else:
        print("Deletion canceled.\n")

def search_contacts():
    term = input("Enter search term: ").strip()
    if not term:
        print("Search term cannot be empty!\n")
        return
    display_contacts(filter_term=term)

# =========================
# Bulk Search & Replace
# =========================
def bulk_search_replace():
    global contacts  # << Move this to the top
    if not contacts:
        print("\nNo contacts available for bulk search & replace.\n")
        return

    print("\n--- Bulk Search & Replace ---")
    field = input("Choose field to update (name/phone/email): ").strip().lower()
    if field not in ['name', 'phone', 'email']:
        print("Invalid field. Choose 'name', 'phone', or 'email'.")
        return

    search_text = input("Enter text to search: ").strip()
    replace_text = input("Enter replacement text: ").strip()

    if not search_text:
        print("Search text cannot be empty!")
        return

    # Keep track of changes for preview
    changes = []
    updated_contacts = {}

    for name, info in contacts.items():
        if field == "name":
            if re.search(re.escape(search_text), name, re.IGNORECASE):
                new_name = re.sub(re.escape(search_text), replace_text, name, flags=re.IGNORECASE)
                updated_contacts[new_name] = info
                changes.append(f"{name} -> {new_name}")
            else:
                updated_contacts[name] = info
        else:
            value = info.get(field, "")
            if re.search(re.escape(search_text), value, re.IGNORECASE):
                new_value = re.sub(re.escape(search_text), replace_text, value, flags=re.IGNORECASE)
                info[field] = new_value
                changes.append(f"{name}: {field} -> {new_value}")
            updated_contacts[name] = info

    if not changes:
        print("No matches found for the given search text.\n")
        return

    # Preview changes
    print("\nPreview of changes:")
    print("-" * 40)
    for change in changes:
        print(change)
    print("-" * 40)

    confirm = input("Apply these changes? (y/n): ").strip().lower()
    if confirm == 'y':
        contacts = updated_contacts
        save_contacts()
        print(f"{len(changes)} changes applied successfully.\n")
    else:
        print("Bulk replacement canceled.\n")

# =========================
# Main Menu
# =========================
def main_menu():
    load_contacts()
    while True:
        print("\n=== Contact Book CLI ===")
        print("1. Display all contacts")
        print("2. Add contact")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Search contacts")
        print("6. Bulk Search & Replace")
        print("7. Exit")
        choice = input("Choose an option [1-7]: ").strip()
        
        if choice == '1':
            display_contacts()
        elif choice == '2':
            add_contact()
        elif choice == '3':
            update_contact()
        elif choice == '4':
            delete_contact()
        elif choice == '5':
            search_contacts()
        elif choice == '6':
            bulk_search_replace()
        elif choice == '7':
            print("Exiting Contact Book. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.\n")

# =========================
# Run Program
# =========================
if __name__ == "__main__":
    main_menu()
