# 🟢 Deal ID Audit Tool - Streamlit Edition

## Quick Start Guide

### Installation Steps

#### Step 1: Verify Python Installation
```powershell
python --version
```
Should show Python 3.8 or higher. If not installed, download from [python.org](https://python.org)

#### Step 2: Install Dependencies
Choose one method:

**Option A - Automatic Setup (Windows)**
```powershell
.\setup.ps1
```

**Option B - Manual Installation**
```powershell
pip install -r requirements.txt
```

#### Step 3: Run the Application
```powershell
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`

---

## Application Features

### 📊 Three Main Tabs

#### 1. **Single Deal Audit**
- Interactive form-based validation
- Real-time feedback on each parameter
- Detailed check results with visual indicators
- Recommendations for remediation

**How to use:**
1. Fill in all deal parameters
2. Select checkboxes for KVPs, devices, and geo targets
3. Enter floor price and audience segments
4. Click "Run Audit"
5. Review results with color-coded validation checks

#### 2. **Batch Audit**
- Upload CSV files with multiple deals
- Process large volumes at once
- Get summary results table
- Download audit results

**CSV Format Required:**
```
deal_id,status,buyer_seat_id,msft_refresh,brand_safety,inventory_type,geo,devices,segments,deal_list_id,floor_price,creative_approved,inventory_strength,historical_performance
D-1001,Active,BS-12345,true,true,true,US;CA,mobile;desktop,tech_enthusiasts,DL-9876,5.50,true,Strong,Good
```

#### 3. **Audit History**
- View all previous audits from current session
- Expand audit records to see detailed results
- Track deal performance over time
- Review recommendations

---

## Validation Rules

### Market Standards
- **CPM Price Range**: $2.00 - $15.00
- **Maximum Segments**: 5 (exceeding is flagged as restrictive)
- **Minimum Requirements**: All fields must be completed

### Required KVPs (All 3 must be checked)
- `msft_refresh` - Microsoft refresh flag
- `brand_safety` - Brand safety setting
- `inventory_type` - Type of inventory

### Valid Geographic Targets
US, CA, GB, DE, FR, AU, JP, IN, BR, MX

### Valid Device Types
mobile, desktop, tablet

### Inventory Strength Levels
- **Strong** ✅ (PASS)
- **Moderate** ✅ (PASS)
- **Weak** ❌ (FAIL - insufficient)

### Historical Performance Levels
- **Good** ✅ (PASS)
- **Mixed** ✅ (PASS)  
- **Poor** ❌ (FAIL)

---

## Audit Scoring System

The tool evaluates 9 critical validation checks:

1. **Deal Status** - Must be "Active"
2. **Buyer Seat ID** - Must be present and non-empty
3. **KVPs** - All 3 required KVPs must be selected
4. **Targeting** - Geo codes, devices, and segments must be valid
5. **Deal List ID** - Must be approved and present
6. **Floor Price** - Must fall within $2-$15 CPM range
7. **Creative Audit** - Creative must be approved
8. **Inventory** - Must be Strong or Moderate strength
9. **Historical Performance** - Must be Good or Mixed

### Scoring Formula
```
Outcome Percentage = (Checks Passed / 9) × 100

HIGH ✅     ≥ 90% - Ready for launch
MEDIUM ⚠️  60-89% - Needs remediation
LOW ❌      < 60% - Significant issues
```

---

## Example Workflows

### Auditing a Single Deal
1. Open Streamlit app
2. Go to "Single Deal Audit" tab
3. Fill in: D-1001
4. Select: Active status
5. Enter: BS-12345
6. Check: All 3 KVPs
7. Check: US, CA (Geo)
8. Check: Mobile, Desktop (Devices)
9. Enter: 5.50 (Floor Price)
10. Select: DL-9876 (Deal List ID)
11. Check: Creative Approved
12. Select: Strong (Inventory)
13. Select: Good (Historical)
14. Click: "Run Audit"
15. Review: GREEN/HIGH outcome ✅

### Batch Processing Deals
1. Prepare CSV file with deal data
2. Go to "Batch Audit" tab
3. Upload CSV file
4. Click "Run Batch Audit"
5. View results summary
6. See individual deal outcomes

### Reviewing Past Audits
1. Go to "Audit History" tab
2. Click on deal you want to review
3. See detailed validation results
4. Check recommendations provided

---

## Troubleshooting

### Python Not Found
```
Error: 'python' is not recognized as an internal or external command
```
**Solution**: Install Python from [python.org](https://python.org) and add to PATH

### Streamlit Not Found
```
Error: 'streamlit' is not recognized
```
**Solution**: Run installation:
```powershell
pip install streamlit
```

### Port Already in Use
```
Error: Address already in use (:8501)
```
**Solution**: Streamlit will automatically use a different port (8502, 8503, etc.)

### File Upload Error
```
Error: Invalid file format
```
**Solution**: Ensure CSV file has correct headers and format

---

## Advanced Usage

### Custom Market Benchmarks
Edit `app.py` to change validation rules:
```python
MARKET_CPM_RANGE = {'min': 2.0, 'max': 15.0}  # Adjust as needed
REQUIRED_KVPS = ['msft_refresh', 'brand_safety', 'inventory_type']  # Add/remove as needed
VALID_COUNTRY_CODES = [...]  # Add/remove countries
```

### Adding New Validation Checks
1. Add new method to `DealAuditor` class
2. Call method in `validate_deal()`
3. Add to results display in appropriate tab

---

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 512 MB minimum
- **Disk Space**: ~200 MB (including dependencies)
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)
- **Internet**: Required for initial Streamlit setup

---

## Performance Notes

- Single deal audits: <100ms
- Batch audits: Depends on file size (typically 50-100 deals/second)
- Audit history: Cleared when session ends
- To persist history: Export results as CSV

---

## Support & Documentation

For more information:
- [Streamlit Docs](https://docs.streamlit.io)
- [Pandas Docs](https://pandas.pydata.org)
- Review audit recommendations for deal remediation

---

## File Structure

```
c:\Users\pastormarta\Vscode\
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── setup.ps1             # PowerShell setup script
├── setup.bat             # Batch setup script
├── README_STREAMLIT.md   # This file
├── Untitled-1.ipynb      # Jupyter notebook (data analysis)
├── vite.config.js        # Vite config (legacy)
├── index.html            # HTML entry (legacy)
├── package.json          # NPM config (legacy)
└── src/                  # Legacy web files
    ├── main.js
    └── style.css
```
