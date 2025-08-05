from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import json
import os
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import shutil

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        return restricted_party

    def update_customer(self, customer_id: int, data: dict):
        """Update an existing customer"""
        customer = next((c for c in self.customers if c["id"] == customer_id), None)
        if customer:
            customer.update(data)
            customer["modified_date"] = datetime.now().isoformat()
            self.save_data(self.customers, self.customers_file)
            return customer
        return None

    def update_restricted_party(self, party_id: int, data: dict):
        """Update an existing restricted party"""
        party = next((p for p in self.restricted_parties if p["id"] == party_id), None)
        if party:
            party.update(data)
            party["modified_date"] = datetime.now().isoformat()
            self.save_data(self.restricted_parties, self.restricted_parties_file)
            return party
        return None

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
                    exact_matches.append({
                        "customer": customer,
                        "restricted_party": party,
                        "similarity": 1.0,
                        "match_type": "exact",
                        "hold_type": None,
                        "match_date": datetime.now().isoformat()
                    })

        return exact_matches

    def run_screening(self):
        """Run screening to find both similar and exact matches"""
        exact_matches = self.find_exact_matches()
        similar_matches = self.find_similar_matches()
        all_matches = exact_matches + similar_matches

        self.matches = all_matches
        self.save_data(self.matches, self.matches_file)

        return all_matches

    def update_hold_type(self, match_index: int, hold_type: str, dtype: str = None):
        """Update hold type for exact matches"""
        if 0 <= match_index < len(self.matches):
            self.matches[match_index]["hold_type"] = hold_type
            if dtype:
                self.matches[match_index]["dtype"] = dtype
            self.save_data(self.matches, self.matches_file)
            return True
        return False

    def import_customers_from_excel(self, file_path: str):
        """Import customers from Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            imported_count = 0
            errors = []

            # Check if required columns exist
            required_columns = ['Name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return 0, f"Missing required columns: {', '.join(missing_columns)}. Available columns: {', '.join(df.columns.tolist())}"

            # Process each row
            for index, row in df.iterrows():
                try:
                    name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ''
                    if name:  # Only import if name is not empty
                        address = str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else ''
                        phone = str(row.get('Phone', '')).strip() if pd.notna(row.get('Phone')) else ''
                        email = str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else ''
                        comments = str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else ''

                        self.add_customer(name, address, phone, email, comments)
                        imported_count += 1
                    else:
                        errors.append(f"Row {index + 2}: Name is empty")
                except Exception as row_error:
                    errors.append(f"Row {index + 2}: {str(row_error)}")

            if errors and imported_count == 0:
                return 0, f"No customers imported. Errors: {'; '.join(errors[:5])}"
            elif errors:
                return imported_count, f"Imported {imported_count} customers with some errors: {'; '.join(errors[:3])}"

            return imported_count, None
        except Exception as e:
            return 0, f"Error reading Excel file: {str(e)}. Please ensure the file is a valid Excel file with a 'Name' column."

    def import_restricted_parties_from_excel(self, file_path: str):
        """Import restricted parties from Excel file"""
        try:
            df = pd.read_excel(file_path)
            imported_count = 0

            for index, row in df.iterrows():
                name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ''
                if name:  # Only import if name is not empty
                    reason = str(row.get('Reason', '')).strip() if pd.notna(row.get('Reason')) else ''
                    source = str(row.get('Source', '')).strip() if pd.notna(row.get('Source')) else ''
                    comments = str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else ''

                    self.add_restricted_party(name, reason, source, comments)
                    imported_count += 1

            return imported_count, None
        except Exception as e:
            return 0, str(e)

# Initialize the tool
tool = CustomerRestrictedPartyTool()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
def customers():
    return render_template('customers.html', customers=tool.customers)

@app.route('/restricted-parties')
def restricted_parties():
    return render_template('restricted_parties.html', parties=tool.restricted_parties)



@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/comments')
def comments():
    return render_template('comments.html')

@app.route('/country-codes')
def country_codes():
    return render_template('country_codes.html')



@app.route('/api/customers', methods=['GET', 'POST'])
def api_customers():
    if request.method == 'POST':
        data = request.json
        customer = tool.add_customer(
            data.get('name', ''),
            data.get('address', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('comments', '')
        )
        return jsonify(customer)
    return jsonify(tool.customers)

@app.route('/api/customers/<int:customer_id>', methods=['PUT', 'DELETE'])
def api_update_customer(customer_id):
    if request.method == 'DELETE':
        # Delete customer
        customer_index = next((i for i, c in enumerate(tool.customers) if c["id"] == customer_id), None)
        if customer_index is not None:
            deleted_customer = tool.customers.pop(customer_index)
            tool.save_data(tool.customers, tool.customers_file)
            return jsonify({'success': True, 'deleted_customer': deleted_customer})
        return jsonify({'error': 'Customer not found'}), 404

    # PUT request
    data = request.json
    customer = tool.update_customer(customer_id, data)
    if customer:
        return jsonify(customer)
    return jsonify({'error': 'Customer not found'}), 404

@app.route('/api/restricted-parties', methods=['GET', 'POST'])
def api_restricted_parties():
    if request.method == 'POST':
        data = request.json
        party = tool.add_restricted_party(
            data.get('name', ''),
            data.get('reason', ''),
            data.get('source', ''),
            data.get('comments', '')
        )
        return jsonify(party)
    return jsonify(tool.restricted_parties)

@app.route('/api/restricted-parties/<int:party_id>', methods=['PUT', 'DELETE'])
def api_update_restricted_party(party_id):
    if request.method == 'DELETE':
        # Delete restricted party
        party_index = next((i for i, p in enumerate(tool.restricted_parties) if p["id"] == party_id), None)
        if party_index is not None:
            deleted_party = tool.restricted_parties.pop(party_index)
            tool.save_data(tool.restricted_parties, tool.restricted_parties_file)
            return jsonify({'success': True, 'deleted_party': deleted_party})
        return jsonify({'error': 'Restricted party not found'}), 404

    # PUT request
    data = request.json
    party = tool.update_restricted_party(party_id, data)
    if party:
        return jsonify(party)
    return jsonify({'error': 'Restricted party not found'}), 404



@app.route('/api/upload-customers', methods=['POST'])
def upload_customers():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Check if file was saved successfully
            if not os.path.exists(file_path):
                return jsonify({'error': 'Failed to save uploaded file'}), 500

            imported_count, error = tool.import_customers_from_excel(file_path)

            # Clean up uploaded file
            try:
                os.remove(file_path)
            except OSError:
                pass  # File cleanup failed, but don't fail the request

            if error:
                return jsonify({'error': error}), 400

            if imported_count == 0:
                return jsonify({'error': 'No customers were imported. Please check your Excel file format.'}), 400

            return jsonify({'success': True, 'imported_count': imported_count})

        return jsonify({'error': 'Invalid file type. Please upload .xlsx or .xls files'}), 400

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/upload-restricted-parties', methods=['POST'])
def upload_restricted_parties():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        imported_count, error = tool.import_restricted_parties_from_excel(file_path)

        # Clean up uploaded file
        os.remove(file_path)

        if error:
            return jsonify({'error': f'Error importing data: {error}'}), 400

        return jsonify({'success': True, 'imported_count': imported_count})

    return jsonify({'error': 'Invalid file type. Please upload .xlsx or .xls files'}), 400

@app.route('/download/standalone')
def download_standalone():
    """Download the standalone tool"""
    return send_file('standalone_tool.py', as_attachment=True, download_name='customer_screening_tool.py')

@app.route('/download/zip')
def download_zip():
    """Download the entire project as ZIP"""
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'customer_screening_tool.zip')

        # Files and directories to include in the ZIP
        files_to_include = [
            'app.py',
            'main.py',
            'standalone_tool.py',
            'README.md',
            'requirements.txt',
            'pyproject.toml',
            'customers.json',
            'restricted_parties.json',
            'matches.json',
            'templates/',
            'static/' if os.path.exists('static') else None
        ]

        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in files_to_include:
                if item is None:
                    continue

                if os.path.isfile(item):
                    zipf.write(item, item)
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)

        return send_file(zip_path, as_attachment=True, download_name='customer_screening_tool.zip')

    except Exception as e:
        return jsonify({'error': f'Error creating ZIP file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)