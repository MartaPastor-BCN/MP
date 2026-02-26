# 🟢 Deal ID Audit Tool

A comprehensive validation system for programmatic deals with interactive audit capabilities.

## Features

✅ **9-Point Validation** - Complete deal validation against market standards
- Deal Status verification
- Buyer Seat ID validation
- Key-Value Pairs (KVPs) checking
- Targeting attributes validation (Geo, Devices, Segments)
- Deal List ID approval
- Floor Price competitive analysis ($2-$15 CPM range)
- Creative audit status
- Inventory match assessment
- Historical performance review

✅ **Single Deal Audit** - Interactive form-based audit for individual deals
✅ **Batch Audit** - Upload CSV files to audit multiple deals simultaneously
✅ **Audit History** - Track all previous audits with detailed results
✅ **Data Analysis** - Jupyter Notebook with Python implementation

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup

1. Clone or download the project

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Usage

### Single Deal Audit
1. Navigate to the **Single Deal Audit** tab
2. Fill in all deal parameters
3. Click **Run Audit**
4. View comprehensive validation results with pass/fail indicators

### Batch Audit
1. Navigate to the **Batch Audit** tab
2. Upload a CSV file with multiple deals
3. CSV should contain columns: `deal_id`, `status`, `buyer_seat_id`, `kvps_*`, `geo`, `devices`, `segments`, `deal_list_id`, `floor_price`, `creative_approved`, `inventory_strength`, `historical_performance`
4. Click **Run Batch Audit**
5. Download results as CSV

### Audit History
- All audits are automatically saved to the session history
- Review previous audits with full details and recommendations

## Market Standards

- **CPM Range**: $2.00 - $15.00
- **Required KVPs**: msft_refresh, brand_safety, inventory_type
- **Valid Device Types**: mobile, desktop, tablet
- **Valid Countries**: US, CA, GB, DE, FR, AU, JP, IN, BR, MX
- **Max Segments**: 5 (restrictive if exceeded)

## Audit Outcomes

- **HIGH ✅** (90%+): Deal ready for launch
- **MEDIUM ⚠️** (60-89%): Address flagged issues before launch
- **LOW ❌** (<60%): Significant remediation required

## Files

- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `Untitled-1.ipynb` - Jupyter Notebook with data analysis tools
- `src/` - Legacy Vite web application (optional)

## Example Deal Data

```python
{
    'status': 'Active',
    'buyer_seat_id': 'BS-12345',
    'kvps': {
        'msft_refresh': True,
        'brand_safety': True,
        'inventory_type': True
    },
    'targeting': {
        'geo': ['US', 'CA', 'GB'],
        'devices': ['mobile', 'desktop'],
        'segments': ['tech_enthusiasts', 'finance_professionals']
    },
    'deal_list_id': 'DL-9876',
    'floor_price': 5.50,
    'creative_approved': True,
    'inventory_strength': 'Strong',
    'historical_performance': 'Good'
}
```

## Support

For issues or improvements, refer to the audit recommendations provided in the application.
