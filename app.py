import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import json
from io import BytesIO

# ================================================================================
# VERSION & BRANDING
# ================================================================================
APP_VERSION = "2.0 - MONETIZE SEAT 280 ONLY"
APP_TITLE = "Monetize Guaranteed Media Planning"

# ================================================================================
# CURRENCY MAPPING BY REGION
# ================================================================================
REGION_CURRENCY = {
    "US": ("USD", "$"),
    "CA": ("CAD", "$"),
    "UK": ("GBP", "£"),
    "DE": ("EUR", "€"),
    "FR": ("EUR", "€"),
    "NL": ("EUR", "€"),
    "ES": ("EUR", "€"),
    "IT": ("EUR", "€"),
    "BE": ("EUR", "€"),
    "AT": ("EUR", "€"),
    "SE": ("EUR", "€"),
    "AU": ("AUD", "$"),
    "NZ": ("AUD", "$"),
    "SG": ("SGD", "$"),
    "IN": ("INR", "₹"),
    "JP": ("JPY", "¥"),
    "BR": ("BRL", "R$"),
    "MX": ("MXN", "$"),
}

def get_currency_symbol(market):
    """Get currency symbol based on market code."""
    return REGION_CURRENCY.get(market.upper(), ("USD", "$"))[1]

# ================================================================================
# PRODUCT RULES - MONETIZE GUARANTEED ONLY (SEAT 280)
# ================================================================================
PRODUCT_RULES = {
    "Programmatic Guaranteed - First Impression": {
        "publisher": "MSN",
        "ad_formats": ["Banner"],
        "device_scopes": ["All Devices", "Desktop", "Mobile"],
        "line_item_type": "PG",
        "priority": 7,
        "revenue_type": "CPM",
        "pacing": "ASAP",
        "frequency_cap": "1 impression per user per day",
        "inventory_type": "Banner",
        "geo_targeting": "Country targeting required",
        "publisher_targeting": "KV pub = msn",
        "seat": "280 - Monetize"
    },
    "Programmatic Guaranteed - Standard": {
        "publisher": ["MSN", "Outlook"],
        "ad_formats": ["Banner", "Native"],
        "device_scopes": ["All Devices", "Desktop", "Mobile"],
        "line_item_type": "PG",
        "priority": 5,
        "revenue_type": "CPM",
        "pacing": "Even",
        "frequency_cap": "6 impressions per user per day",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": {
            "MSN": "KV pub=msn",
            "Outlook": "Direct Inventory - Outlook Native"
        },
        "seat": "280 - Monetize"
    },
    "GDALI - Guaranteed Campaign (Impressions)": {
        "publisher": ["MSN", "Outlook"],
        "ad_formats": ["Banner", "Native"],
        "device_scopes": ["All Devices", "Desktop", "Mobile"],
        "line_item_type": "Guaranteed (GDALI)",
        "priority": 5,
        "revenue_type": "CPM",
        "pacing": "Even",
        "frequency_cap": "6 impressions per user per day",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": {
            "MSN": "KV pub=msn",
            "Outlook": "Direct Inventory - Outlook Native"
        },
        "seat": "280 - Monetize"
    },
    "GDALI - Takeover (MSN Homepage)": {
        "publisher": "MSN",
        "ad_formats": ["Banner"],
        "device_scopes": ["Desktop"],
        "line_item_type": "Guaranteed (GDALI)",
        "priority": 15,
        "revenue_type": "Cost Per Day",
        "pacing": "00:00 to 23:59",
        "frequency_cap": "Off",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn, sales_page_type=homepage",
        "seat": "280 - Monetize"
    },
    "GDALI - Takeover (Outlook Banner)": {
        "publisher": "Outlook",
        "ad_formats": ["Banner"],
        "device_scopes": ["Desktop"],
        "line_item_type": "Guaranteed (GDALI)",
        "priority": 15,
        "revenue_type": "Cost Per Day",
        "pacing": "00:00 to 23:59",
        "frequency_cap": "Off",
        "inventory_type": "Banner",
        "geo_targeting": "None",
        "publisher_targeting": "Outlook Banner",
        "seat": "280 - Monetize"
    },
    "GDALI - Takeover (Outlook Native)": {
        "publisher": "Outlook",
        "ad_formats": ["Native"],
        "device_scopes": ["All Devices"],
        "line_item_type": "Guaranteed (GDALI)",
        "priority": 15,
        "revenue_type": "Cost Per Day",
        "pacing": "00:00 to 23:59",
        "frequency_cap": "Off",
        "inventory_type": "Native",
        "geo_targeting": "Country required",
        "publisher_targeting": "Publisher=Outlook Native (1000230)",
        "seat": "280 - Monetize"
    },
    "PG - High Impact": {
        "publisher": "MSN",
        "ad_formats": ["Banner"],
        "device_scopes": ["Desktop"],
        "line_item_type": "PG",
        "priority": 15,
        "revenue_type": "CPM",
        "pacing": "Even",
        "frequency_cap": "Off",
        "inventory_type": "Banner",
        "geo_targeting": "Country required",
        "publisher_targeting": "KV pub=msn",
        "seat": "280 - Monetize"
    }
}

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================
def get_compatible_formats(product, publisher="MSN"):
    """Get compatible formats based on product and publisher."""
    # Outlook is Native only
    if publisher == "Outlook":
        return ["Native"]
    # MSN has all formats
    return ["Banner", "Native", "Video"]

def get_compatible_devices(product):
    return PRODUCT_RULES[product]["device_scopes"]

def get_publisher_targeting(product, publisher):
    """Get the correct publisher targeting based on product and selected publisher."""
    rules = PRODUCT_RULES[product]
    pub_target = rules.get("publisher_targeting", "")
    
    # If publisher_targeting is a dict, get the value for the selected publisher
    if isinstance(pub_target, dict):
        return pub_target.get(publisher, "Not available for this publisher")
    
    # Otherwise return the string value
    return pub_target

def generate_o_o_taxonomy(market, publisher, product, ad_format, device):
    """O&O Naming Taxonomy"""
    device_clean = device.replace(" ", "")
    if "First Impression" in product:
        return f"{market}_{publisher}_First Impression_{ad_format}_{device_clean}_PG_Imps"
    elif "High Impact" in product:
        return f"{market}_{publisher}_High Impact_{ad_format}_{device_clean}_PG_Imps"
    elif "Takeover" in product:
        return f"{market}_{publisher}_Takeover_{ad_format}_{device_clean}_GDALI_SOV"
    elif "Standard" in product:
        return f"{market}_{publisher}_Standard_{ad_format}_{device_clean}_PG_Imps"
    else:
        return f"{market}_{publisher}_{product}_{ad_format}_{device_clean}"

def generate_li_name(market, publisher, product, ad_format, device):
    """Line Item Name"""
    device_clean = device.replace(" ", "")
    prod_label = product.split("-")[0].strip() if "-" in product else product
    return f"{market}_{publisher}_{prod_label}_{ad_format}_{device_clean}"

def calculate_flight_days(start, end):
    return (end - start).days + 1

def calculate_cost(volume, rate, is_takeover, flight_days=1):
    if is_takeover:
        return flight_days * rate
    return (volume / 1000) * rate

def create_excel_export(flights_list):
    """Create Excel file with multiple flights/campaigns."""
    wb = Workbook()
    ws = wb.active
    ws.title = "MediaPlan"
    
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=10)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    headers = ["Advertiser", "Campaign", "Market", "Publisher", "Product", 
               "Format", "Device", "Start", "End", "Rate Type", 
               "Rate", "Volume", "Total Cost", "O&O Taxonomy"]
    
    for i, h in enumerate(headers, 1):
        cell = ws.cell(1, i)
        cell.value = h
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # Add rows for each flight
    for row_idx, flight in enumerate(flights_list, 2):
        flight_days = flight.get("flight_days", calculate_flight_days(flight["start_date"], flight["end_date"]))
        is_takeover = "Takeover" in flight["product"]
        rate_type = "CPD" if is_takeover else "CPM"
        volume = flight_days if is_takeover else flight.get("volume", 0)
        total_cost = flight.get("total_cost", calculate_cost(flight.get("volume", 0), flight["rate"], is_takeover, flight_days))
        currency = flight.get("currency", get_currency_symbol(flight["market"]))
        
        row_data = [
            flight["advertiser"],
            flight["campaign"],
            flight["market"],
            flight["publisher"],
            flight["product"],
            flight["format"],
            flight["device"],
            flight["start_date"].strftime("%Y-%m-%d"),
            flight["end_date"].strftime("%Y-%m-%d"),
            rate_type,
            f"{currency}{flight['rate']:.2f}",
            f"{volume:,.0f}" if isinstance(volume, int) else volume,
            f"{currency}{total_cost:,.2f}",
            flight.get("taxonomy", "")
        ]
        
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row_idx, col_idx)
            cell.value = val
            cell.border = border
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    
    # Set column widths
    for i in range(1, len(headers) + 1):
        col_letter = get_column_letter(i)
        ws.column_dimensions[col_letter].width = 16
    
    ws.freeze_panes = "A2"
    return wb

# ================================================================================
# STREAMLIT CONFIGURATION
# ================================================================================
st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="collapsed")

# Initialize session state for multiple flights
if "flights" not in st.session_state:
    st.session_state.flights = []

# Header with version
st.markdown(f"# 🎯 {APP_TITLE}")
st.markdown(f"**Version:** {APP_VERSION}", help="Monetize Seat 280 | Guaranteed Delivery Only | No PMP | No Curate")
st.info("💡 **CPM rates must be aligned with DNV Rate Card**")
st.divider()

# ================================================================================
# SECTION 1: CAMPAIGN DETAILS - MINIMALIST 4-COLUMN LAYOUT
# ================================================================================
st.subheader("📋 Campaign Details")

c1, c2, c3, c4 = st.columns(4)
with c1:
    market = st.text_input("Market", value="UK", placeholder="e.g. UK, US, DE")
with c2:
    advertiser = st.text_input("Advertiser", value="Acme Corp")
with c3:
    campaign = st.text_input("Campaign", value="Q1 2026")
with c4:
    pub = st.selectbox("Publisher", ["MSN", "Outlook"])

c1, c2, c3, c4 = st.columns(4)
with c1:
    product = st.selectbox("Product", [
        "Programmatic Guaranteed - First Impression",
        "Programmatic Guaranteed - Standard",
        "PG - High Impact",
        "GDALI - Guaranteed Campaign (Impressions)",
        "GDALI - Takeover (MSN Homepage)",
        "GDALI - Takeover (Outlook Banner)",
        "GDALI - Takeover (Outlook Native)"
    ])
with c2:
    device = st.selectbox("Device", get_compatible_devices(product))
with c3:
    fmt = st.selectbox("Format", get_compatible_formats(product, pub))
with c4:
    start_date = st.date_input("Start Date")

end_date = st.date_input("End Date")

# ================================================================================
# SECTION 2: O&O NAMING TAXONOMY
# ================================================================================
st.subheader("📝 O&O Naming Taxonomy")

taxonomy = generate_o_o_taxonomy(market, pub, product, fmt, device)
li_name = generate_li_name(market, pub, product, fmt, device)

tax_col1, tax_col2 = st.columns(2)
with tax_col1:
    st.code(taxonomy, language="text")
with tax_col2:
    st.code(li_name, language="text")

# ================================================================================
# SECTION 3: PRICING WITH CURRENCY
# ================================================================================
st.subheader("💰 Pricing")

rules = PRODUCT_RULES[product]
currency = get_currency_symbol(market)
is_takeover = "Takeover" in product

price_col1, price_col2 = st.columns(2)

volume = 0
with price_col1:
    if is_takeover:
        st.markdown("**Rate Type**")
        st.write("Cost Per Day")
        daily_rate = st.number_input(f"Daily Rate ({currency})", value=100.0, min_value=0.01, step=1.0)
        rate = daily_rate
    else:
        st.markdown("**Rate Type**")
        st.write("CPM")
        cpm = st.number_input(f"CPM ({currency})", value=10.0, min_value=0.01, step=0.50)
        impressions = st.number_input("Impressions", value=100000, min_value=1, step=1000)
        rate = cpm
        volume = impressions

# ================================================================================
# SECTION 4: TARGETING RULES (PRODUCT-LOCKED)
# ================================================================================
st.subheader("🔒 Targeting Rules (Locked by Product)")

tgt_col1, tgt_col2, tgt_col3 = st.columns(3)

with tgt_col1:
    st.markdown(f"**Seat:** {rules['seat']}")
    st.markdown(f"**Priority:** {rules['priority']}")
    st.markdown(f"**Frequency Cap:** {rules['frequency_cap']}")

with tgt_col2:
    st.markdown(f"**Pacing:** {rules['pacing']}")
    st.markdown(f"**Inventory Type:** {rules['inventory_type']}")
    st.markdown(f"**Geo Targeting:** {rules['geo_targeting']}")

with tgt_col3:
    st.markdown(f"**Publisher Targeting:** {get_publisher_targeting(product, pub)}")
    st.markdown(f"**Line Item Type:** {rules['line_item_type']}")
    st.markdown(f"**Revenue Type:** {rules['revenue_type']}")

# ================================================================================
# SECTION 5: PLAN SUMMARY & EXPORT
# ================================================================================
st.divider()
st.subheader("📊 Plan Summary")

# Validation
if end_date < start_date:
    st.error("❌ End Date must be >= Start Date")
    st.stop()

flight_days = calculate_flight_days(start_date, end_date)
total_cost = calculate_cost(volume, rate, is_takeover, flight_days)

summary_cols = {
    "Market": market,
    "Publisher": pub,
    "Product": product[:35],
    "Format": fmt,
    "Device": device,
    "Start": start_date.strftime("%Y-%m-%d"),
    "End": end_date.strftime("%Y-%m-%d"),
    "Days": flight_days,
    "Rate Type": "CPD" if is_takeover else "CPM",
    "Rate": f"{currency}{rate:.2f}",
    "Volume": f"{volume:,.0f}" if not is_takeover else f"{flight_days} days",
    "Total Cost": f"{currency}{total_cost:,.2f}",
    "O&O Taxonomy": taxonomy
}

summary_df = pd.DataFrame([summary_cols])
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Monetize Setup
st.subheader("⚙️ Monetize Setup")
setup_text = f"""
• **Seat:** {rules['seat']}
• **Line Item Type:** {rules['line_item_type']}
• **Delivery:** {'Exclusive' if is_takeover else 'Standard'}
• **Priority:** {rules['priority']}
• **Pacing:** {rules['pacing']}
• **Frequency Cap:** {rules['frequency_cap']}
• **Publisher Targeting:** {get_publisher_targeting(product, pub)}
• **Inventory Type:** {rules['inventory_type']}
• **Geo Targeting:** {rules['geo_targeting']}
"""
st.markdown(setup_text)

# ================================================================================
# MULTIPLE FLIGHTS SECTION
# ================================================================================
st.subheader("✈️ Manage Multiple Flights")

# Campaign base details (same for all flights)
st.markdown(f"**Campaign Structure:** {product} | {fmt} | {device} | {pub}")
st.markdown("---")

# Section to add new flights with different dates and budgets
st.markdown("**➕ Add New Flight (Same Product, Different Dates & Budget)**")

new_flight_col1, new_flight_col2, new_flight_col3, new_flight_col4 = st.columns(4)

with new_flight_col1:
    new_start = st.date_input("Flight Start Date", value=start_date, key="new_start")

with new_flight_col2:
    new_end = st.date_input("Flight End Date", value=end_date, key="new_end")

with new_flight_col3:
    if "Takeover" in product:
        new_rate = st.number_input(f"Daily Rate ({currency})", value=rate, min_value=0.01, step=1.0, key="new_rate")
        new_volume = 0
    else:
        new_rate = st.number_input(f"CPM ({currency})", value=rate, min_value=0.01, step=0.50, key="new_rate")
        new_volume = st.number_input("Impressions", value=volume, min_value=1, step=1000, key="new_volume")

with new_flight_col4:
    add_flight_btn = st.button("➕ Add This Flight", use_container_width=True)

if add_flight_btn:
    if new_end < new_start:
        st.error("❌ Flight End Date must be >= Start Date")
    else:
        new_flight_days = calculate_flight_days(new_start, new_end)
        new_total_cost = calculate_cost(new_volume, new_rate, "Takeover" in product, new_flight_days)
        
        flight_data = {
            "advertiser": advertiser,
            "campaign": campaign,
            "publisher": pub,
            "product": product,
            "format": fmt,
            "device": device,
            "start_date": new_start,
            "end_date": new_end,
            "market": market,
            "rate": new_rate,
            "volume": new_volume,
            "taxonomy": generate_o_o_taxonomy(market, pub, product, fmt, device),
            "li_name": generate_li_name(market, pub, product, fmt, device),
            "flight_days": new_flight_days,
            "total_cost": new_total_cost,
            "currency": currency
        }
        st.session_state.flights.append(flight_data)
        st.success(f"✅ Flight added! Total flights: {len(st.session_state.flights)}")
        st.rerun()

# Display added flights
if st.session_state.flights:
    st.subheader(f"📋 Added Flights ({len(st.session_state.flights)})")
    for i, flight in enumerate(st.session_state.flights):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            flight_days = flight.get("flight_days", 1)
            rate_type = "CPD" if "Takeover" in flight["product"] else "CPM"
            st.write(f"**Flight {i+1}:** {flight['start_date'].strftime('%Y-%m-%d')} → {flight['end_date'].strftime('%Y-%m-%d')} | {flight_days} days | {rate_type} {flight['currency']}{flight['rate']:.2f} | Total: {flight['currency']}{flight['total_cost']:,.2f}")
        with col2:
            st.write("")  # Spacer
        with col3:
            if st.button("❌ Remove", key=f"remove_{i}", use_container_width=True):
                st.session_state.flights.pop(i)
                st.rerun()

# ================================================================================
# EXPORT SECTION
# ================================================================================
st.subheader("📥 Export Media Plan")

# Use added flights if available, otherwise use current configuration
if st.session_state.flights:
    flights_to_export = st.session_state.flights
    st.info(f"📤 Exporting {len(flights_to_export)} flight(s)")
else:
    # Create a single flight entry from current configuration
    flights_to_export = [{
        "advertiser": advertiser,
        "campaign": campaign,
        "publisher": pub,
        "start_date": start_date,
        "end_date": end_date,
        "market": market,
        "product": product,
        "format": fmt,
        "device": device,
        "rate": rate,
        "volume": volume,
        "taxonomy": taxonomy,
        "flight_days": flight_days,
        "total_cost": total_cost,
        "currency": currency
    }]

json_export = {
    "Advertiser": advertiser,
    "Campaign": campaign,
    "Market": market,
    "Publisher": pub,
    "FlightsCount": len(flights_to_export),
    "Flights": [
        {
            "Product": flight["product"],
            "Format": flight["format"],
            "Device": flight["device"],
            "Start": flight["start_date"].strftime("%Y-%m-%d"),
            "End": flight["end_date"].strftime("%Y-%m-%d"),
            "RateType": "CPD" if "Takeover" in flight["product"] else "CPM",
            "Rate": float(flight["rate"]),
            "TotalCost": float(flight.get("total_cost", 0)),
            "Taxonomy": flight.get("taxonomy", ""),
            "Seat": "280 - Monetize"
        }
        for flight in flights_to_export
    ]
}

ex_col1, ex_col2 = st.columns(2)

with ex_col1:
    excel_wb = create_excel_export(flights_to_export)
    excel_bytes = BytesIO()
    excel_wb.save(excel_bytes)
    excel_bytes.seek(0)
    st.download_button(
        label="📊 Download Excel",
        data=excel_bytes.getvalue(),
        file_name="Microsoft_Advertising_MediaPlan_generated.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with ex_col2:
    json_str = json.dumps(json_export, indent=2)
    st.download_button(
        label="📄 Download JSON",
        data=json_str,
        file_name="media_plan.json",
        mime="application/json"
    )

# ================================================================================
# FOOTER
# ================================================================================
st.divider()
st.markdown("**Monetize Seat 280 - Guaranteed Delivery Only**", help="No PMP | No Curate | No Open Auction")
st.markdown("*Last Updated: Feb 26, 2026*")
