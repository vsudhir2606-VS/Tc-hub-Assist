
#!/usr/bin/env python3
"""
Customer & Restricted Party Screening Tool - Standalone Version
A downloadable tool for screening customers against restricted parties lists.
"""

import json
import os
import sys
import pandas as pd
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
        print(f"✅ Customer '{name}' added successfully!")
        return customer

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
        print(f"✅ Restricted party '{name}' added successfully!")
        return restricted_party

    def delete_customer(self, customer_id: int):
        """Delete a customer"""
        customer_index = next((i for i, c in enumerate(self.customers) if c["id"] == customer_id), None)
        if customer_index is not None:
            deleted_customer = self.customers.pop(customer_index)
            self.save_data(self.customers, self.customers_file)
            print(f"✅ Customer '{deleted_customer['name']}' deleted successfully!")
            return True
        print("❌ Customer not found!")
        return False

    def delete_restricted_party(self, party_id: int):
        """Delete a restricted party"""
        party_index = next((i for i, p in enumerate(self.restricted_parties) if p["id"] == party_id), None)
        if party_index is not None:
            deleted_party = self.restricted_parties.pop(party_index)
            self.save_data(self.restricted_parties, self.restricted_parties_file)
            print(f"✅ Restricted party '{deleted_party['name']}' deleted successfully!")
            return True
        print("❌ Restricted party not found!")
        return False

    def edit_customer(self, customer_id: int):
        """Edit an existing customer"""
        customer = next((c for c in self.customers if c["id"] == customer_id), None)
        if not customer:
            print("❌ Customer not found!")
            return

        print(f"\n📝 Editing Customer: {customer['name']}")
        print("Press Enter to keep current value")
        
        customer["name"] = input(f"Name ({customer['name']}): ").strip() or customer["name"]
        customer["address"] = input(f"Address ({customer['address']}): ").strip() or customer["address"]
        customer["phone"] = input(f"Phone ({customer['phone']}): ").strip() or customer["phone"]
        customer["email"] = input(f"Email ({customer['email']}): ").strip() or customer["email"]
        customer["comments"] = input(f"Comments ({customer['comments']}): ").strip() or customer["comments"]
        customer["modified_date"] = datetime.now().isoformat()

        self.save_data(self.customers, self.customers_file)
        print("✅ Customer updated successfully!")

    def edit_restricted_party(self, party_id: int):
        """Edit an existing restricted party"""
        party = next((p for p in self.restricted_parties if p["id"] == party_id), None)
        if not party:
            print("❌ Restricted party not found!")
            return

        print(f"\n📝 Editing Restricted Party: {party['name']}")
        print("Press Enter to keep current value")
        
        party["name"] = input(f"Name ({party['name']}): ").strip() or party["name"]
        party["reason"] = input(f"Reason ({party['reason']}): ").strip() or party["reason"]
        party["source"] = input(f"Source ({party['source']}): ").strip() or party["source"]
        party["comments"] = input(f"Comments ({party['comments']}): ").strip() or party["comments"]
        party["modified_date"] = datetime.now().isoformat()

        self.save_data(self.restricted_parties, self.restricted_parties_file)
        print("✅ Restricted party updated successfully!")

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

    def find_similar_matches(self, threshold: float = 0.3):
        """Find customers with similar names to restricted parties"""
        similar_matches = []
        
        for customer in self.customers:
            for party in self.restricted_parties:
                similarity = self.calculate_similarity(customer["name"], party["name"])
                if similarity >= threshold and similarity < 1.0:
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
                    print(f"\n🚨 EXACT MATCH FOUND 🚨")
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
            print("\n🔒 Select hold type:")
            print("1. Mandatory Hold")
            print("2. Conditional Hold")
            
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                return "mandatory"
            elif choice == "2":
                return "conditional"
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")

    def display_matches(self, matches: List[Dict]):
        """Display all matches"""
        if not matches:
            print("ℹ️  No matches found.")
            return

        print(f"\n🔍 Found {len(matches)} match(es):")
        print("=" * 80)

        for i, match in enumerate(matches, 1):
            print(f"\n📋 Match {i}")
            print(f"Match Type: {match['match_type'].upper()}")
            print(f"Similarity: {match['similarity']:.2%}")
            
            if match['match_type'] == 'exact':
                print(f"🔒 Hold Type: {match['hold_type'].upper()}")
            
            print(f"\n👤 Customer:")
            customer = match['customer']
            print(f"  Name: {customer['name']}")
            print(f"  Address: {customer.get('address', 'N/A')}")
            print(f"  Phone: {customer.get('phone', 'N/A')}")
            print(f"  Email: {customer.get('email', 'N/A')}")
            print(f"  Comments: {customer.get('comments', 'N/A')}")
            
            print(f"\n🚫 Restricted Party:")
            party = match['restricted_party']
            print(f"  Name: {party['name']}")
            print(f"  Reason: {party.get('reason', 'N/A')}")
            print(f"  Source: {party.get('source', 'N/A')}")
            print(f"  Comments: {party.get('comments', 'N/A')}")
            print("-" * 80)

    def run_screening(self):
        """Run screening to find both similar and exact matches"""
        print("🔍 Running screening...")
        
        exact_matches = self.find_exact_matches()
        similar_matches = self.find_similar_matches()
        
        all_matches = exact_matches + similar_matches
        
        self.matches = all_matches
        self.save_data(self.matches, self.matches_file)
        
        print(f"\n✅ Screening complete!")
        print(f"Found {len(exact_matches)} exact matches")
        print(f"Found {len(similar_matches)} similar matches")
        
        return all_matches

    def display_all_customers(self):
        """Display all customers"""
        if not self.customers:
            print("ℹ️  No customers found.")
            return
            
        print(f"\n👥 ALL CUSTOMERS ({len(self.customers)} total)")
        print("=" * 80)
        for customer in self.customers:
            print(f"\nID: {customer['id']}")
            print(f"Name: {customer['name']}")
            print(f"Address: {customer.get('address', 'N/A')}")
            print(f"Phone: {customer.get('phone', 'N/A')}")
            print(f"Email: {customer.get('email', 'N/A')}")
            print(f"Comments: {customer.get('comments', 'N/A')}")
            print("-" * 40)

    def display_all_restricted_parties(self):
        """Display all restricted parties"""
        if not self.restricted_parties:
            print("ℹ️  No restricted parties found.")
            return
            
        print(f"\n🚫 ALL RESTRICTED PARTIES ({len(self.restricted_parties)} total)")
        print("=" * 80)
        for party in self.restricted_parties:
            print(f"\nID: {party['id']}")
            print(f"Name: {party['name']}")
            print(f"Reason: {party.get('reason', 'N/A')}")
            print(f"Source: {party.get('source', 'N/A')}")
            print(f"Comments: {party.get('comments', 'N/A')}")
            print("-" * 40)

    def import_customers_from_excel(self, file_path: str):
        """Import customers from Excel file"""
        try:
            df = pd.read_excel(file_path)
            imported_count = 0
            
            for index, row in df.iterrows():
                name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ''
                if name:
                    address = str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else ''
                    phone = str(row.get('Phone', '')).strip() if pd.notna(row.get('Phone')) else ''
                    email = str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else ''
                    comments = str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else ''
                    
                    self.add_customer(name, address, phone, email, comments)
                    imported_count += 1
            
            print(f"✅ Successfully imported {imported_count} customers from Excel!")
            return imported_count, None
        except Exception as e:
            error_msg = f"Error importing Excel file: {str(e)}"
            print(f"❌ {error_msg}")
            return 0, error_msg

    def import_restricted_parties_from_excel(self, file_path: str):
        """Import restricted parties from Excel file"""
        try:
            df = pd.read_excel(file_path)
            imported_count = 0
            
            for index, row in df.iterrows():
                name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ''
                if name:
                    reason = str(row.get('Reason', '')).strip() if pd.notna(row.get('Reason')) else ''
                    source = str(row.get('Source', '')).strip() if pd.notna(row.get('Source')) else ''
                    comments = str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else ''
                    
                    self.add_restricted_party(name, reason, source, comments)
                    imported_count += 1
            
            print(f"✅ Successfully imported {imported_count} restricted parties from Excel!")
            return imported_count, None
        except Exception as e:
            error_msg = f"Error importing Excel file: {str(e)}"
            print(f"❌ {error_msg}")
            return 0, error_msg

    def export_to_excel(self):
        """Export all data to Excel files"""
        try:
            # Export customers
            if self.customers:
                customers_df = pd.DataFrame(self.customers)
                customers_df.to_excel('customers_export.xlsx', index=False)
                print("✅ Customers exported to customers_export.xlsx")
            
            # Export restricted parties
            if self.restricted_parties:
                parties_df = pd.DataFrame(self.restricted_parties)
                parties_df.to_excel('restricted_parties_export.xlsx', index=False)
                print("✅ Restricted parties exported to restricted_parties_export.xlsx")
            
            # Export matches
            if self.matches:
                matches_df = pd.DataFrame(self.matches)
                matches_df.to_excel('matches_export.xlsx', index=False)
                print("✅ Matches exported to matches_export.xlsx")
                
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")

    def main_menu(self):
        """Main menu for the application"""
        print("🚀 Starting Customer & Restricted Party Screening Tool...")
        
        while True:
            print("\n" + "="*60)
            print("🛡️  CUSTOMER & RESTRICTED PARTY SCREENING TOOL")
            print("="*60)
            print("1.  Add Customer")
            print("2.  Add Restricted Party")
            print("3.  Edit Customer")
            print("4.  Edit Restricted Party")
            print("5.  Delete Customer")
            print("6.  Delete Restricted Party")
            print("7.  View All Customers")
            print("8.  View All Restricted Parties")
            print("9.  Import Customers from Excel")
            print("10. Import Restricted Parties from Excel")
            print("11. Export Data to Excel")
            print("12. Run Screening (Find Matches)")
            print("13. View Previous Matches")
            print("14. Exit")
            
            choice = input("\nEnter your choice (1-14): ").strip()
            
            try:
                if choice == "1":
                    name = input("Customer Name: ").strip()
                    if name:
                        address = input("Address (optional): ").strip()
                        phone = input("Phone (optional): ").strip()
                        email = input("Email (optional): ").strip()
                        comments = input("Comments (optional): ").strip()
                        self.add_customer(name, address, phone, email, comments)
                    else:
                        print("❌ Name is required!")
                        
                elif choice == "2":
                    name = input("Restricted Party Name: ").strip()
                    if name:
                        reason = input("Reason (optional): ").strip()
                        source = input("Source (optional): ").strip()
                        comments = input("Comments (optional): ").strip()
                        self.add_restricted_party(name, reason, source, comments)
                    else:
                        print("❌ Name is required!")
                        
                elif choice == "3":
                    self.display_all_customers()
                    customer_id = int(input("\nEnter Customer ID to edit: "))
                    self.edit_customer(customer_id)
                        
                elif choice == "4":
                    self.display_all_restricted_parties()
                    party_id = int(input("\nEnter Restricted Party ID to edit: "))
                    self.edit_restricted_party(party_id)

                elif choice == "5":
                    self.display_all_customers()
                    customer_id = int(input("\nEnter Customer ID to delete: "))
                    self.delete_customer(customer_id)

                elif choice == "6":
                    self.display_all_restricted_parties()
                    party_id = int(input("\nEnter Restricted Party ID to delete: "))
                    self.delete_restricted_party(party_id)
                        
                elif choice == "7":
                    self.display_all_customers()
                    
                elif choice == "8":
                    self.display_all_restricted_parties()

                elif choice == "9":
                    file_path = input("Enter Excel file path: ").strip()
                    if os.path.exists(file_path):
                        self.import_customers_from_excel(file_path)
                    else:
                        print("❌ File not found!")

                elif choice == "10":
                    file_path = input("Enter Excel file path: ").strip()
                    if os.path.exists(file_path):
                        self.import_restricted_parties_from_excel(file_path)
                    else:
                        print("❌ File not found!")

                elif choice == "11":
                    self.export_to_excel()
                    
                elif choice == "12":
                    matches = self.run_screening()
                    self.display_matches(matches)
                    
                elif choice == "13":
                    self.display_matches(self.matches)
                    
                elif choice == "14":
                    print("👋 Thank you for using the screening tool!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {str(e)}")

def main():
    """Main function to run the standalone tool"""
    print("🛡️  Customer & Restricted Party Screening Tool - Standalone Version")
    print("=" * 70)
    
    # Check if required dependencies are available
    try:
        import pandas as pd
        print("✅ All dependencies are available")
    except ImportError:
        print("❌ Missing dependency: pandas")
        print("Please install with: pip install pandas openpyxl")
        sys.exit(1)
    
    tool = CustomerRestrictedPartyTool()
    tool.main_menu()

if __name__ == "__main__":
    main()
