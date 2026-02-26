import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import json
from io import BytesIO

# ================================================================================
# PAGE CONFIG & STYLING
# ================================================================================
st.set_page_config(
    page_title="Monetize Guaranteed Media Planning",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { padding: 2rem 1rem; }
    .stButton > button { width: 100%; padding: 0.5rem; font-weight: bold; }
    h1 { color: #0078D4; font-size: 2.5rem; margin-bottom: 0.25rem; }
    h2 { color: #0078D4; font-size: 1.5rem; margin-top: 1.5rem; margin-bottom: 0.75rem; border-bottom: 2px solid #0078D4; padding-bottom: 0.5rem; }
    .warning-box { background-color: #FFF4CE; padding: 1rem; border-left: 4px solid #FF9800; border-radius: 4px; margin: 1rem 0; }
    .info-box { background-color: #E3F2FD; padding: 1rem; border-left: 4px solid #0078D4; border-radius: 4px; margin: 1rem 0; }
    .checklist { background-color: #F5F5F5; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ================================================================================
# 1. HEADER / VERSIONING
# ================================================================================
st.markdown("# Monetize Guaranteed Media Planning")
st.markdown("**Version:** 2.0 – MONETIZE SEAT 280 ONLY")

st.markdown("""
<div class="warning-box">
    <strong>⚠️ Important:</strong> CPM rates must be aligned with DNV Rate Card. This tool enforces Seat 280 Guaranteed Delivery Only.
</div>
""", unsafe_allow_html=True)

# ================================================================================
# INITIALIZE SESSION STATE
# ================================================================================
if "flights" not in st.session_state:
    st.session_state.flights = []
if "campaign_details" not in st.session_state:
    st.session_state.campaign_details = {}

# ================================================================================
# PRODUCT RULES - MONETIZE GUARANTEED ONLY (SEAT 280)
# ================================================================================
PRODUCT_RULES = {
    "Programmatic Guaranteed - First Impression": {
        "seat": "280 - Monetize",
        "priority": 7,
        "frequency_cap": "1 impression per user per day",
        "pacing": "ASAP",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub = msn",
        "line_item_type": "PG",
        "revenue_type": "CPM",
        "publishers": ["MSN"],
        "formats": ["Banner"]
    },
    "Programmatic Guaranteed - Standard": {
        "seat": "280 - Monetize",
        "priority": 5,
        "frequency_cap": "6 impressions per user per day",
        "pacing": "Even",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn (MSN) | Direct Inventory - Outlook Native (Outlook)",
        "line_item_type": "PG",
        "revenue_type": "CPM",
        "publishers": ["MSN", "Outlook"],
        "formats": ["Banner", "Native"]
    },
    "High Impact": {
        "seat": "280 - Monetize",
        "priority": 15,
        "frequency_cap": "2 impressions per user per day",
        "pacing": "Even",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn",
        "line_item_type": "PG",
        "revenue_type": "CPM",
        "publishers": ["MSN"],
        "formats": ["Banner"]
    },
    "GDALI - Impressions": {
        "seat": "280 - Monetize",
        "priority": 5,
        "frequency_cap": "6 impressions per user per day",
        "pacing": "Even",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn (MSN) | Direct Inventory - Outlook Native (Outlook)",
        "line_item_type": "Guaranteed (GDALI)",
        "revenue_type": "CPM",
        "publishers": ["MSN", "Outlook"],
        "formats": ["Banner", "Native"]
    },
    "GDALI - MSN Takeover": {
        "seat": "280 - Monetize",
        "priority": 15,
        "frequency_cap": "1 impression per user per day",
        "pacing": "ASAP",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn",
        "line_item_type": "Guaranteed (GDALI)",
        "revenue_type": "CPM",
        "publishers": ["MSN"],
        "formats": ["Banner"]
    },
    "GDALI - Outlook Takeover": {
        "seat": "280 - Monetize",
        "priority": 15,
        "frequency_cap": "1 impression per user per day",
        "pacing": "ASAP",
        "inventory_type": "Native",
        "geo_targeting": "Country required",
        "publisher_targeting": "Direct Inventory - Outlook Native",
        "line_item_type": "Guaranteed (GDALI)",
        "revenue_type": "CPM",
        "publishers": ["Outlook"],
        "formats": ["Native"]
    },
    "PG - Programmatic Guaranteed (Video)": {
        "seat": "280 - Monetize",
        "priority": 10,
        "frequency_cap": "2 impressions per user per day",
        "pacing": "Even",
        "inventory_type": "Video",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn",
        "line_item_type": "PG",
        "revenue_type": "CPM",
        "publishers": ["MSN"],
        "formats": ["Video"]
    }
}



# ================================================================================
# HELPER FUNCTIONS
# ================================================================================
def get_currency_symbol(market):
    """Get currency symbol based on market code."""
    return REGION_CURRENCY.get(market.upper(), ("USD", "$"))[1]

def get_compatible_formats(product, publisher):
    """Get compatible formats based on product and publisher."""
    product_info = PRODUCT_RULES.get(product, {})
    formats = product_info.get("formats", [])
    
    if publisher == "Outlook":
        return [f for f in formats if f == "Native"] or ["Native"]
    else:
        return formats

def generate_o_o_taxonomy(market, publisher, product, ad_format, device):
    """Generate O&O Naming Taxonomy."""
    device_code = {"All Devices": "AllDevices", "Desktop": "Desktop", "Mobile": "Mobile", "Tablet": "Tablet"}.get(device, "AllDevices")
    return f"{market}_{publisher}_{product}_{ad_format}_{device_code}_PG_Imps"

def generate_li_name(advertiser, market, publisher, product):
    """Generate Line Item Name."""
    return f"{advertiser}_{market}_{publisher}_{product}"

def create_excel_export(flights_list, campaign_info):
    """Create Excel file with campaign data."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Campaign"
    
    header_fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    ws.merge_cells("A1:K1")
    title = ws["A1"]
    title.value = "Microsoft Advertising - Monetize Guaranteed Media Plan"
    title.font = Font(bold=True, size=14, color="0078D4")
    
    ws["A2"] = "Campaign Name"
    ws["B2"] = campaign_info.get("campaign", "")
    ws["A3"] = "Advertiser"
    ws["B3"] = campaign_info.get("advertiser", "")
    ws["A4"] = "Market"
    ws["B4"] = campaign_info.get("market", "")
    ws["C4"] = "Publisher"
    ws["D4"] = campaign_info.get("publisher", "")
    
    headers = ["Flight", "Product", "Format", "Device", "Start Date", "End Date", 
               "Volume", "CPM", "Currency", "Total Cost", "Seat"]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=6, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    for row_idx, flight in enumerate(flights_list, 7):
        ws.cell(row=row_idx, column=1).value = flight.get("flight_num", 1)
        ws.cell(row=row_idx, column=2).value = flight.get("product", "")
        ws.cell(row=row_idx, column=3).value = flight.get("format", "")
        ws.cell(row=row_idx, column=4).value = flight.get("device", "")
        start_str = flight.get("start_date", "").strftime("%Y-%m-%d") if hasattr(flight.get("start_date"), "strftime") else flight.get("start_date", "")
        ws.cell(row=row_idx, column=5).value = start_str
        end_str = flight.get("end_date", "").strftime("%Y-%m-%d") if hasattr(flight.get("end_date"), "strftime") else flight.get("end_date", "")
        ws.cell(row=row_idx, column=6).value = end_str
        ws.cell(row=row_idx, column=7).value = flight.get("volume", 0)
        ws.cell(row=row_idx, column=8).value = flight.get("cpm", 0)
        ws.cell(row=row_idx, column=9).value = flight.get("currency", "$")
        ws.cell(row=row_idx, column=10).value = flight.get("total_cost", 0)
        ws.cell(row=row_idx, column=11).value = "280"
    
    ws.freeze_panes = "A7"
    
    for col in range(1, 12):
        ws.column_dimensions[get_column_letter(col)].width = 15
    
    return wb

# ================================================================================
# 2. CAMPAIGN DETAILS (INPUTS)
# ================================================================================
st.markdown("## 2) Campaign Details")

col1, col2, col3, col4 = st.columns(4)

with col1:
    market = st.selectbox(
        "Market",
        list(REGION_CURRENCY.keys()),
        key="market",
        help="Country/Region for campaign"
    )
    st.session_state.campaign_details["market"] = market

with col2:
    advertiser = st.text_input(
        "Advertiser",
        value=st.session_state.campaign_details.get("advertiser", ""),
        key="advertiser",
        help="Client/Advertiser name"
    )
    st.session_state.campaign_details["advertiser"] = advertiser

with col3:
    campaign = st.text_input(
        "Campaign",
        value=st.session_state.campaign_details.get("campaign", ""),
        key="campaign",
        help="Campaign name/ID"
    )
    st.session_state.campaign_details["campaign"] = campaign

with col4:
    publisher = st.selectbox(
        "Publisher",
        ["MSN", "Outlook"],
        key="publisher",
        help="Target publisher"
    )
    st.session_state.campaign_details["publisher"] = publisher

col5, col6, col7, col8 = st.columns(4)

with col5:
    device = st.selectbox(
        "Device",
        ["All Devices", "Desktop", "Mobile", "Tablet"],
        key="device",
        help="Target device type"
    )
    st.session_state.campaign_details["device"] = device

with col6:
    product = st.selectbox(
        "Product",
        list(PRODUCT_RULES.keys()),
        key="product",
        help="Monetize Guaranteed product"
    )
    st.session_state.campaign_details["product"] = product

with col7:
    ad_format = st.selectbox(
        "Format",
        get_compatible_formats(product, publisher),
        key="format",
        help="Ad format (locked by product/publisher)"
    )
    st.session_state.campaign_details["format"] = ad_format

with col8:
    st.write("")

col9, col10 = st.columns(2)

with col9:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now().date(),
        key="start_date"
    )
    st.session_state.campaign_details["start_date"] = start_date

with col10:
    end_date = st.date_input(
        "End Date",
        value=datetime.now().date() + timedelta(days=30),
        key="end_date"
    )
    st.session_state.campaign_details["end_date"] = end_date

# ================================================================================
# 3. O&O NAMING TAXONOMY
# ================================================================================
st.markdown("## 3) O&O Naming Taxonomy")

taxonomy = generate_o_o_taxonomy(market, publisher, product, ad_format, device)
li_name = generate_li_name(advertiser or "ADVERTISER", market, publisher, product)

col_tax1, col_tax2 = st.columns(2)

with col_tax1:
    st.markdown("**Generated Taxonomy:**")
    st.code(taxonomy, language="text")

with col_tax2:
    st.markdown("**Line Item Name:**")
    st.code(li_name, language="text")

st.markdown("<div class='info-box'><strong>ℹ️ Note:</strong> These auto-generated names follow Microsoft Advertising standards for Monetize Guaranteed campaigns.</div>", unsafe_allow_html=True)

# ================================================================================
# 4. PRICING
# ================================================================================
st.markdown("## 4) Pricing")

currency_sym = get_currency_symbol(market)
currency_code = REGION_CURRENCY.get(market.upper(), ("USD", "$"))[0]

col_price1, col_price2, col_price3, col_price4 = st.columns(4)

with col_price1:
    rate_type = st.radio("Rate Type", ["CPM", "CPD"], horizontal=True)

with col_price2:
    if rate_type == "CPM":
        rate_value = st.number_input(
            f"CPM ({currency_sym})",
            min_value=0.0,
            value=10.0,
            step=0.01,
            key="cpm_value"
        )
    else:
        rate_value = st.number_input(
            f"CPD ({currency_sym})",
            min_value=0.0,
            value=50.0,
            step=1.0,
            key="cpd_value"
        )

with col_price3:
    if rate_type == "CPM":
        impressions = st.number_input(
            "Impressions",
            min_value=0,
            value=100000,
            step=1000,
            key="impressions"
        )
        total_cost = (impressions / 1000) * rate_value
    else:
        days = (end_date - start_date).days + 1
        total_cost = days * rate_value
        st.write(f"Days: {days}")

with col_price4:
    st.write(f"**Total Cost: {currency_sym}{total_cost:,.2f}**")

st.markdown(f"<div class='warning-box'><strong>DNV Rate Card Check:</strong> CPM ({currency_sym}{rate_value}) must be aligned with DNV Rate Card for {market}.</div>", unsafe_allow_html=True)

# ================================================================================
# 5. TARGETING RULES (LOCKED BY PRODUCT)
# ================================================================================
st.markdown("## 5) Targeting Rules (Locked by Product)")

product_config = PRODUCT_RULES.get(product, {})

st.markdown("**Product Configuration (Non-editable):**")

col_rule1, col_rule2, col_rule3, col_rule4 = st.columns(4)

with col_rule1:
    st.metric("Seat", product_config.get("seat", "280"))

with col_rule2:
    st.metric("Priority", product_config.get("priority", "-"))

with col_rule3:
    st.metric("Pacing", product_config.get("pacing", "Even"))

with col_rule4:
    st.metric("Revenue Type", product_config.get("revenue_type", "CPM"))

rules_data = {
    "Frequency Cap": product_config.get("frequency_cap", "N/A"),
    "Inventory Type": product_config.get("inventory_type", "N/A"),
    "Geo Targeting": product_config.get("geo_targeting", "N/A"),
    "Publisher Targeting": product_config.get("publisher_targeting", "N/A"),
    "Line Item Type": product_config.get("line_item_type", "N/A"),
}

st.markdown("**Targeting Details:**")
for key, value in rules_data.items():
    st.write(f"• **{key}:** {value}")

# ================================================================================
# 6. MONETIZE SETUP (COMPACT CHECKLIST)
# ================================================================================
st.markdown("## 6) Monetize Setup Summary")

setup_summary = f"""
Seat 280 • {product_config.get('line_item_type', 'PG')} • Priority {product_config.get('priority', '-')} 
• Pacing: {product_config.get('pacing', 'Even')} • Freq Cap: {product_config.get('frequency_cap', 'N/A')} 
• Publisher: {product_config.get('publisher_targeting', 'N/A')} 
• Format: {ad_format} • Location: {market} • Inventory: {product_config.get('inventory_type', 'N/A')}
"""

st.markdown(f"<div class='checklist'>{setup_summary}</div>", unsafe_allow_html=True)

# ================================================================================
# 7. MANAGE MULTIPLE FLIGHTS
# ================================================================================
st.markdown("## 7) Manage Multiple Flights")

st.write(f"**Current Flights:** {len(st.session_state.flights)}")

if st.button("➕ Add New Flight (Same Product, Different Dates & Budget)", use_container_width=True):
    new_flight = {
        "flight_num": len(st.session_state.flights) + 1,
        "product": product,
        "format": ad_format,
        "device": device,
        "start_date": start_date,
        "end_date": end_date,
        "volume": impressions if rate_type == "CPM" else 0,
        "cpm": rate_value if rate_type == "CPM" else 0,
        "currency": currency_sym,
        "total_cost": total_cost
    }
    st.session_state.flights.append(new_flight)
    st.success(f"Flight {new_flight['flight_num']} added!")

if st.session_state.flights:
    st.markdown("**Existing Flights:**")
    for idx, flight in enumerate(st.session_state.flights):
        col_flight1, col_flight2, col_flight3 = st.columns([3, 1, 1])
        
        with col_flight1:
            st.write(f"**Flight {flight['flight_num']}** | {flight['product']} | {flight['start_date']} to {flight['end_date']}")
        
        with col_flight2:
            st.write(f"{flight['currency']}{flight['total_cost']:,.2f}")
        
        with col_flight3:
            if st.button("🗑️ Remove", key=f"remove_flight_{idx}"):
                st.session_state.flights.pop(idx)
                st.rerun()

# ================================================================================
# 8. EXPORT MEDIA PLAN
# ================================================================================
st.markdown("## 8) Export Media Plan")

st.write("Download your finalized media plan in Excel or JSON format:")

col_export1, col_export2 = st.columns(2)

export_flights = st.session_state.flights if st.session_state.flights else [
    {
        "flight_num": 1,
        "product": product,
        "format": ad_format,
        "device": device,
        "start_date": start_date,
        "end_date": end_date,
        "volume": impressions if rate_type == "CPM" else 0,
        "cpm": rate_value if rate_type == "CPM" else 0,
        "currency": currency_sym,
        "total_cost": total_cost
    }
]

with col_export1:
    excel_file = create_excel_export(export_flights, st.session_state.campaign_details)
    excel_bytes = BytesIO()
    excel_file.save(excel_bytes)
    excel_bytes.seek(0)
    
    st.download_button(
        label="📥 Download Excel",
        data=excel_bytes.getvalue(),
        file_name="Microsoft_Advertising_MediaPlan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_export2:
    json_data = {
        "campaign": st.session_state.campaign_details,
        "flights": export_flights,
        "generated_at": datetime.now().isoformat()
    }
    
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(json_data, indent=2, default=str),
        file_name="Microsoft_Advertising_MediaPlan.json",
        mime="application/json",
        use_container_width=True
    )

st.divider()

st.markdown(f"""
<div class='info-box'>
<strong>Monetize Seat 280 – Guaranteed Delivery Only</strong><br>
Last Updated: {datetime.now().strftime('%b %d, %Y')}
</div>
""", unsafe_allow_html=True)
