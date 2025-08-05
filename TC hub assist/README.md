
# Customer & Restricted Party Screening Tool

A comprehensive tool for screening customers against restricted parties lists, available as both a web application and a standalone downloadable version.

## 🌐 Web Application Version

The web application is already running on Replit and provides a user-friendly interface for managing customers, restricted parties, and running screenings.

### Features:
- ✅ Customer management (add, edit, delete, import from Excel)
- ✅ Restricted parties management
- ✅ Automated screening with similarity matching
- ✅ Real-time search and comparison
- ✅ Comments and country codes lookup
- ✅ Excel import/export functionality
- ✅ Interactive web interface

### Usage:
1. The web app is currently running on port 5000
2. Navigate through the different sections using the navigation menu
3. Import data from Excel files or add entries manually
4. Run screening to find matches between customers and restricted parties

### Deployment:
To deploy the web app publicly on Replit:
1. Click the **Deploy** button in Replit
2. Choose **Autoscale** deployment
3. Use the default configuration
4. Set run command to: `python app.py`
5. Your app will be live and accessible via a public URL

## 💻 Standalone Downloadable Version

The standalone version (`standalone_tool.py`) is a command-line application that can be downloaded and run on any computer.

### Features:
- ✅ All core functionality from the web version
- ✅ Command-line interface
- ✅ Excel import/export
- ✅ Data persistence with JSON files
- ✅ Enhanced user experience with emojis and formatting
- ✅ Runs offline - no internet required
- ✅ Cross-platform compatibility (Windows, Mac, Linux)

### Requirements:
```bash
pip install pandas openpyxl
```

### Installation & Usage:

1. **Download the standalone tool:**
   - Download `standalone_tool.py` from this repository
   - Place it in a folder where you want to store your data

2. **Install dependencies:**
   ```bash
   pip install pandas openpyxl
   ```

3. **Run the tool:**
   ```bash
   python standalone_tool.py
   ```

4. **Using the tool:**
   - Follow the interactive menu
   - Data is automatically saved to JSON files in the same directory
   - Import/export Excel files as needed
   - Run screenings to find matches

### Menu Options:
1. **Add Customer** - Add new customer records
2. **Add Restricted Party** - Add new restricted party records
3. **Edit Customer** - Modify existing customer information
4. **Edit Restricted Party** - Modify existing restricted party information
5. **Delete Customer** - Remove customer records
6. **Delete Restricted Party** - Remove restricted party records
7. **View All Customers** - Display all customer records
8. **View All Restricted Parties** - Display all restricted party records
9. **Import Customers from Excel** - Bulk import customer data
10. **Import Restricted Parties from Excel** - Bulk import restricted party data
11. **Export Data to Excel** - Export all data to Excel files
12. **Run Screening** - Find matches between customers and restricted parties
13. **View Previous Matches** - Display previously found matches
14. **Exit** - Close the application

## 📊 Excel File Format

### For Customers:
| Name | Address | Phone | Email | Comments |
|------|---------|-------|-------|----------|
| John Doe | 123 Main St | 555-0123 | john@email.com | VIP Customer |

### For Restricted Parties:
| Name | Reason | Source | Comments |
|------|---------|--------|----------|
| Bad Actor | Sanctions | OFAC | High Risk |

## 🔍 Screening Process

The tool performs two types of matching:

1. **Exact Matches** - Perfect name matches that require hold type selection:
   - Mandatory Hold
   - Conditional Hold

2. **Similar Matches** - Names with similarity threshold ≥ 30% for review

## 📁 Data Files

The tool creates and maintains these files:
- `customers.json` - Customer database
- `restricted_parties.json` - Restricted parties database  
- `matches.json` - Screening results
- `*_export.xlsx` - Excel export files

## 🚀 Getting Started

### Web Version (Recommended for teams):
- Already running in your Replit environment
- Access via the web interface
- Deploy for public access using Replit's deployment feature

### Standalone Version (Recommended for individual use):
1. Download `standalone_tool.py`
2. Install Python dependencies: `pip install pandas openpyxl`
3. Run: `python standalone_tool.py`
4. Follow the interactive menu

## 🆘 Support

If you encounter any issues:
1. Ensure all dependencies are installed
2. Check that Excel files follow the correct format
3. Verify file permissions for reading/writing data files
4. For the web version, ensure port 5000 is available

Both versions maintain the same core functionality and data compatibility!
