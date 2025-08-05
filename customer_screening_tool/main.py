
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Optional

class CustomerRestrictedPartyTool:
    def __init__(self):
        self.customers_file = "customers.json"
        self.restricted_parties_file = "restricted_parties.json"
        self.matches_file = "matches.json"
        self.customers = self.load_data(self.customers_file)
        self.restricted_parties = self.load_data(self.restricted_parties_file)
        self.matches = self.load_data(self.matches_file)

    def load_data(self, filename: str) -> List[Dict]:
        """Load data from JSON file or return empty list if file doesn't exist"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_data(self, data: List[Dict], filename: str):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def add_customer(self, name: str, address: str = "", phone: str = "", email: str = "", comments: str = ""):
        """Add a new customer"""
        customer = {
            "id": len(self.customers) + 1,
            "name": name.strip(),
            "address": address.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "comments": comments.strip(),
            "created_date": datetime.now().isoformat()
        }
        self.customers.append(customer)
        self.save_data(self.customers, self.customers_file)
        print(f"Customer '{name}' added successfully!")

    def add_restricted_party(self, name: str, reason: str = "", source: str = "", comments: str = ""):
        """Add a new restricted party"""
        restricted_party = {
            "id": len(self.restricted_parties) + 1,
            "name": name.strip(),
            "reason": reason.strip(),
            "source": source.strip(),
            "comments": comments.strip(),
            "created_date": datetime.now().isoformat()
        }
        self.restricted_parties.append(restricted_party)
        self.save_data(self.restricted_parties, self.restricted_parties_file)
        print(f"Restricted party '{name}' added successfully!")

    def edit_customer(self, customer_id: int):
        """Edit an existing customer"""
        customer = next((c for c in self.customers if c["id"] == customer_id), None)
        if not customer:
            print("Customer not found!")
            return

        print(f"\nEditing Customer: {customer['name']}")
        print("Press Enter to keep current value")
        
        customer["name"] = input(f"Name ({customer['name']}): ").strip() or customer["name"]
        customer["address"] = input(f"Address ({customer['address']}): ").strip() or customer["address"]
        customer["phone"] = input(f"Phone ({customer['phone']}): ").strip() or customer["phone"]
        customer["email"] = input(f"Email ({customer['email']}): ").strip() or customer["email"]
        customer["comments"] = input(f"Comments ({customer['comments']}): ").strip() or customer["comments"]
        customer["modified_date"] = datetime.now().isoformat()

        self.save_data(self.customers, self.customers_file)
        print("Customer updated successfully!")

    def edit_restricted_party(self, party_id: int):
        """Edit an existing restricted party"""
        party = next((p for p in self.restricted_parties if p["id"] == party_id), None)
        if not party:
            print("Restricted party not found!")
            return

        print(f"\nEditing Restricted Party: {party['name']}")
        print("Press Enter to keep current value")
        
        party["name"] = input(f"Name ({party['name']}): ").strip() or party["name"]
        party["reason"] = input(f"Reason ({party['reason']}): ").strip() or party["reason"]
        party["source"] = input(f"Source ({party['source']}): ").strip() or party["source"]
        party["comments"] = input(f"Comments ({party['comments']}): ").strip() or party["comments"]
        party["modified_date"] = datetime.now().isoformat()

        self.save_data(self.restricted_parties, self.restricted_parties_file)
        print("Restricted party updated successfully!")

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

    def find_similar_matches(self, threshold: float = 0.7):
        """Find customers with similar names to restricted parties"""
        similar_matches = []
        
        for customer in self.customers:
            for party in self.restricted_parties:
                similarity = self.calculate_similarity(customer["name"], party["name"])
                if similarity >= threshold and similarity < 1.0:  # Similar but not exact match
                    similar_matches.append({
                        "customer": customer,
                        "restricted_party": party,
                        "similarity": similarity,
                        "match_type": "similar",
                        "match_date": datetime.now().isoformat()
                    })
        
        return similar_matches

    def find_exact_matches(self):
        """Find customers with exact name matches to restricted parties"""
        exact_matches = []
        
        for customer in self.customers:
            for party in self.restricted_parties:
                if customer["name"].lower().strip() == party["name"].lower().strip():
                    # Ask for hold type for exact matches
                    print(f"\n*** EXACT MATCH FOUND ***")
                    print(f"Customer: {customer['name']}")
                    print(f"Restricted Party: {party['name']}")
                    
                    hold_type = self.get_hold_type()
                    
                    exact_matches.append({
                        "customer": customer,
                        "restricted_party": party,
                        "similarity": 1.0,
                        "match_type": "exact",
                        "hold_type": hold_type,
                        "match_date": datetime.now().isoformat()
                    })
        
        return exact_matches

    def get_hold_type(self) -> str:
        """Get hold type from user for exact matches"""
        while True:
            print("\nSelect hold type:")
            print("1. Mandatory Hold")
            print("2. Conditional Hold")
            
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                return "mandatory"
            elif choice == "2":
                return "conditional"
            else:
                print("Invalid choice. Please enter 1 or 2.")

    def display_matches(self, matches: List[Dict]):
        """Display all matches"""
        if not matches:
            print("No matches found.")
            return

        for i, match in enumerate(matches, 1):
            print(f"\n--- Match {i} ---")
            print(f"Match Type: {match['match_type'].upper()}")
            print(f"Similarity: {match['similarity']:.2%}")
            
            if match['match_type'] == 'exact':
                print(f"Hold Type: {match['hold_type'].upper()}")
            
            print(f"\nCustomer:")
            customer = match['customer']
            print(f"  Name: {customer['name']}")
            print(f"  Address: {customer.get('address', 'N/A')}")
            print(f"  Phone: {customer.get('phone', 'N/A')}")
            print(f"  Email: {customer.get('email', 'N/A')}")
            print(f"  Comments: {customer.get('comments', 'N/A')}")
            
            print(f"\nRestricted Party:")
            party = match['restricted_party']
            print(f"  Name: {party['name']}")
            print(f"  Reason: {party.get('reason', 'N/A')}")
            print(f"  Source: {party.get('source', 'N/A')}")
            print(f"  Comments: {party.get('comments', 'N/A')}")

    def run_screening(self):
        """Run screening to find both similar and exact matches"""
        print("Running screening...")
        
        # Find exact matches first (with hold type selection)
        exact_matches = self.find_exact_matches()
        
        # Find similar matches
        similar_matches = self.find_similar_matches()
        
        all_matches = exact_matches + similar_matches
        
        # Save matches
        self.matches = all_matches
        self.save_data(self.matches, self.matches_file)
        
        print(f"\nScreening complete!")
        print(f"Found {len(exact_matches)} exact matches")
        print(f"Found {len(similar_matches)} similar matches")
        
        return all_matches

    def display_all_customers(self):
        """Display all customers"""
        if not self.customers:
            print("No customers found.")
            return
            
        print("\n--- ALL CUSTOMERS ---")
        for customer in self.customers:
            print(f"\nID: {customer['id']}")
            print(f"Name: {customer['name']}")
            print(f"Address: {customer.get('address', 'N/A')}")
            print(f"Phone: {customer.get('phone', 'N/A')}")
            print(f"Email: {customer.get('email', 'N/A')}")
            print(f"Comments: {customer.get('comments', 'N/A')}")

    def display_all_restricted_parties(self):
        """Display all restricted parties"""
        if not self.restricted_parties:
            print("No restricted parties found.")
            return
            
        print("\n--- ALL RESTRICTED PARTIES ---")
        for party in self.restricted_parties:
            print(f"\nID: {party['id']}")
            print(f"Name: {party['name']}")
            print(f"Reason: {party.get('reason', 'N/A')}")
            print(f"Source: {party.get('source', 'N/A')}")
            print(f"Comments: {party.get('comments', 'N/A')}")

    def main_menu(self):
        """Main menu for the application"""
        while True:
            print("\n" + "="*50)
            print("CUSTOMER & RESTRICTED PARTY SCREENING TOOL")
            print("="*50)
            print("1. Add Customer")
            print("2. Add Restricted Party")
            print("3. Edit Customer")
            print("4. Edit Restricted Party")
            print("5. View All Customers")
            print("6. View All Restricted Parties")
            print("7. Run Screening (Find Matches)")
            print("8. View Previous Matches")
            print("9. Exit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                name = input("Customer Name: ")
                address = input("Address (optional): ")
                phone = input("Phone (optional): ")
                email = input("Email (optional): ")
                comments = input("Comments (optional): ")
                self.add_customer(name, address, phone, email, comments)
                
            elif choice == "2":
                name = input("Restricted Party Name: ")
                reason = input("Reason (optional): ")
                source = input("Source (optional): ")
                comments = input("Comments (optional): ")
                self.add_restricted_party(name, reason, source, comments)
                
            elif choice == "3":
                self.display_all_customers()
                try:
                    customer_id = int(input("\nEnter Customer ID to edit: "))
                    self.edit_customer(customer_id)
                except ValueError:
                    print("Invalid ID. Please enter a number.")
                    
            elif choice == "4":
                self.display_all_restricted_parties()
                try:
                    party_id = int(input("\nEnter Restricted Party ID to edit: "))
                    self.edit_restricted_party(party_id)
                except ValueError:
                    print("Invalid ID. Please enter a number.")
                    
            elif choice == "5":
                self.display_all_customers()
                
            elif choice == "6":
                self.display_all_restricted_parties()
                
            elif choice == "7":
                matches = self.run_screening()
                self.display_matches(matches)
                
            elif choice == "8":
                self.display_matches(self.matches)
                
            elif choice == "9":
                print("Thank you for using the screening tool!")
                break
                
            else:
                print("Invalid choice. Please try again.")

def main():
    tool = CustomerRestrictedPartyTool()
    tool.main_menu()

if __name__ == "__main__":
    main()
