import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors

# ================================================================================
# PAGE CONFIG & STYLING
# ================================================================================
st.set_page_config(
    page_title="Media Planner Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { padding: 2rem 1.5rem; }
    .stButton > button { 
        padding: 0.6rem 1rem; 
        font-weight: 500; 
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    h2 { 
        color: #0078D4; 
        font-size: 1.4rem; 
        margin-top: 2.5rem; 
        margin-bottom: 1rem; 
        border-bottom: none; 
        padding-bottom: 0;
        letter-spacing: 0.3px;
        font-weight: 600;
    }
    h3 {
        letter-spacing: 0.2px;
        font-weight: 600;
    }
    .info-box { 
        background-color: #FAFAFA; 
        padding: 14px; 
        border-left: 3px solid #0078D4; 
        border-radius: 4px; 
        margin: 1.5rem 0; 
        color: #333; 
        font-size: 0.95rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Table Styling - Subtle Shadows */
    .stDataFrame {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        border: none !important;
    }
    
    /* Spacing */
    .section-spacer {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #FAFAFA;
        border-radius: 6px;
        padding: 0;
        border-left: 3px solid #0078D4;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-value {
        animation: slideUp 0.5s ease-out;
    }
    
    /* Header Gradient */
    .section-header {
        background: linear-gradient(135deg, #0078D4 0%, #0063B1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================================
# 1. HEADER / VERSIONING
# ================================================================================
st.markdown("# Media Planner Tool")
st.markdown("**Monetize Guaranteed - Seat 280** | Version 2.0")

st.markdown("""
<div class="info-box">
    <strong>Guaranteed delivery planning</strong> • CPM rates should align with DNV Rate Card • Seat 280 only
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
    "PG - First Impression": {
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
    "PG - Standard": {
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
    "PG - Video": {
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

def calculate_delivery_pressure(flights_list, product_name, frequency_cap_text=""):
    """
    Calculate delivery success pressure: Low / Medium / High.
    
    Logic:
    - LOW: Duration ≥ 30 days AND Daily Volume ≤ Freq Cap
    - MEDIUM: Duration 14-29 days OR Daily Volume manageable
    - HIGH: Duration < 14 days AND High daily volume, or very constrained
    """
    if not flights_list:
        return "Low", "No flights configured."
    
    total_volume = sum(f.get("volume", 0) for f in flights_list)
    # Get flight duration from first flight (assume all same product)
    first_flight = flights_list[0]
    start = first_flight.get("start_date")
    end = first_flight.get("end_date")
    
    if isinstance(start, str):
        from datetime import datetime
        start = datetime.strptime(start, "%Y-%m-%d").date()
    if isinstance(end, str):
        from datetime import datetime
        end = datetime.strptime(end, "%Y-%m-%d").date()
    
    flight_days = max(1, (end - start).days + 1)
    daily_volume = total_volume / flight_days if flight_days > 0 else total_volume
    
    # Frequency cap extraction (rough: "6 impressions per user per day" -> 6)
    freq_cap = 6  # default
    if "1 impression" in frequency_cap_text.lower():
        freq_cap = 1
    elif "2 impression" in frequency_cap_text.lower():
        freq_cap = 2
    
    # Pressure index
    pressure_ratio = (daily_volume / freq_cap) if freq_cap > 0 else 0
    
    if flight_days >= 30 and pressure_ratio <= 1.0:
        return "Low", f"Flight duration {flight_days} days. Daily volume manageable. Low activation risk."
    elif flight_days >= 14 and pressure_ratio <= 1.5:
        return "Medium", f"Flight duration {flight_days} days. Moderate delivery pressure. Confirm frequency caps and date windows."
    else:
        return "High", f"Flight duration {flight_days} days. High daily volume vs. frequency cap. Escalate to ops team."

def create_internal_excel_export(flights_list, campaign_info, delivery_pressure_label):
    """Create internal-facing Excel with targeting setup and QC checklist."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Internal Setup"
    
    header_fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Header
    ws.merge_cells("A1:M1")
    title = ws["A1"]
    title.value = "Media Plan - Internal Setup & QC"
    title.font = Font(bold=True, size=14, color="0078D4")
    
    # Campaign details
    row = 3
    ws[f"A{row}"] = "Campaign Name:"
    ws[f"B{row}"] = campaign_info.get("campaign", "")
    row += 1
    ws[f"A{row}"] = "Advertiser:"
    ws[f"B{row}"] = campaign_info.get("advertiser", "")
    row += 1
    ws[f"A{row}"] = "Market:"
    ws[f"B{row}"] = campaign_info.get("market", "")
    row += 1
    ws[f"A{row}"] = "Publisher:"
    ws[f"B{row}"] = campaign_info.get("publisher", "")
    row += 1
    ws[f"A{row}"] = "Product:"
    ws[f"B{row}"] = campaign_info.get("product", "")
    
    # Internal Setup Section
    row = 10
    ws[f"A{row}"] = "INTERNAL SETUP & TARGETING"
    ws[f"A{row}"].font = Font(bold=True, size=11, color="0078D4")
    
    row += 2
    headers_setup = ["Field", "Value"]
    for col, header in enumerate(headers_setup, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
        cell.font = Font(bold=True)
    
    row += 1
    setup_fields = [
        ("Seat ID", "280 - Monetize"),
        ("Priority", "5-15"),
        ("Frequency Cap", "Per product rules"),
        ("Pacing", "Even / ASAP"),
        ("KV Parameters", "KV pub=msn (MSN) | Direct (Outlook)"),
        ("Line Item Type", "PG"),
        ("Inventory Type", "Banner / Video / Native"),
        ("Geo Targeting", "Country required"),
    ]
    
    for field_name, field_value in setup_fields:
        ws.cell(row=row, column=1).value = field_name
        ws.cell(row=row, column=2).value = field_value
        row += 1
    
    # QC Checklist
    row += 2
    ws[f"A{row}"] = "QC CHECKLIST"
    ws[f"A{row}"].font = Font(bold=True, size=11, color="0078D4")
    
    row += 2
    total_impressions = sum(f.get("volume", 0) for f in flights_list)
    first_flight = flights_list[0] if flights_list else {}
    start = first_flight.get("start_date")
    end = first_flight.get("end_date")
    if isinstance(start, str):
        from datetime import datetime
        start = datetime.strptime(start, "%Y-%m-%d").date()
    if isinstance(end, str):
        from datetime import datetime
        end = datetime.strptime(end, "%Y-%m-%d").date()
    flight_days = (end - start).days + 1 if start and end else 0
    daily_volume = total_impressions / flight_days if flight_days > 0 else 0
    
    qc_items = [
        ("Delivery Risk Level", delivery_pressure_label),
        ("Total Flights", len(flights_list)),
        ("Flight Duration (days)", flight_days),
        ("Est. Daily Impressions", f"{daily_volume:,.0f}"),
        ("Total Impressions", f"{total_impressions:,.0f}"),
        ("Rate Card Alignment", "⚠️ Verify before IO"),
        ("Publisher Targeting", "KV / Direct Inventory"),
        ("Date Window", f"{start} to {end}"),
    ]
    
    headers_qc = ["Checklist Item", "Status / Value"]
    for col, header in enumerate(headers_qc, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
        cell.font = Font(bold=True)
    
    row += 1
    for item, value in qc_items:
        ws.cell(row=row, column=1).value = item
        ws.cell(row=row, column=2).value = value
        row += 1
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 30
    
    return wb

def create_excel_export(flights_list, campaign_info, delivery_pressure_label, product_config, cpm_rate, currency_sym):
    """Create IO Excel file with Microsoft-style formatting and forecasting table."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Media Plan"
    
    # Colors
    header_fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    subheader_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    subheader_font = Font(bold=True, size=10, color="0078D4")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Title
    ws.merge_cells("A1:F1")
    title = ws["A1"]
    title.value = "MEDIA PLAN - MONETIZE GUARANTEED"
    title.font = Font(bold=True, size=14, color="FFFFFF")
    title.fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 25
    
    # Campaign Details Header
    row = 3
    ws[f"A{row}"] = "Advertiser:"
    ws[f"A{row}"].font = Font(bold=True, size=11)
    ws[f"B{row}"] = campaign_info.get("advertiser", "")
    ws[f"B{row}"].font = Font(size=11)
    
    ws[f"D{row}"] = "Market:"
    ws[f"D{row}"].font = Font(bold=True, size=11)
    ws[f"E{row}"] = campaign_info.get("market", "")
    ws[f"E{row}"].font = Font(size=11)
    
    row = 4
    ws[f"A{row}"] = "Campaign:"
    ws[f"A{row}"].font = Font(bold=True, size=11)
    ws[f"B{row}"] = campaign_info.get("campaign", "")
    ws[f"B{row}"].font = Font(size=11)
    
    ws[f"D{row}"] = "Publisher:"
    ws[f"D{row}"].font = Font(bold=True, size=11)
    ws[f"E{row}"] = campaign_info.get("publisher", "")
    ws[f"E{row}"].font = Font(size=11)
    
    row = 5
    ws[f"A{row}"] = "Order Type:"
    ws[f"A{row}"].font = Font(bold=True, size=11)
    ws[f"B{row}"] = "Insertion Order"
    ws[f"B{row}"].font = Font(size=11)
    
    ws[f"D{row}"] = "Request Date:"
    ws[f"D{row}"].font = Font(bold=True, size=11)
    ws[f"E{row}"] = datetime.now().strftime("%m/%d/%Y")
    ws[f"E{row}"].font = Font(size=11)
    
    # Campaign Overview
    row = 7
    ws[f"A{row}"] = "CAMPAIGN OVERVIEW"
    ws[f"A{row}"].font = Font(bold=True, size=11, color="0078D4")
    
    row = 8
    overview_headers = ["Flight", "Product", "Start Date", "End Date", "Budget", "Total Budget"]
    for col, header in enumerate(overview_headers, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.fill = subheader_fill
        cell.font = subheader_font
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    total_budget = 0
    for row_idx, flight in enumerate(flights_list, 9):
        flight_budget = flight.get('budget', 0)
        total_budget += flight_budget
        
        ws.cell(row=row_idx, column=1).value = flight.get("flight_num", 1)
        ws.cell(row=row_idx, column=2).value = flight.get("product", "")
        
        start_date = flight.get("start_date")
        if hasattr(start_date, "strftime"):
            start_str = start_date.strftime("%m/%d/%Y")
        else:
            start_str = str(start_date)
        ws.cell(row=row_idx, column=3).value = start_str
        
        end_date = flight.get("end_date")
        if hasattr(end_date, "strftime"):
            end_str = end_date.strftime("%m/%d/%Y")
        else:
            end_str = str(end_date)
        ws.cell(row=row_idx, column=4).value = end_str
        
        ws.cell(row=row_idx, column=5).value = f"{flight_budget:,.2f}"
        
        # Total budget in last row
        if row_idx == len(flights_list) + 8:
            ws.cell(row=row_idx, column=6).value = f"{total_budget:,.2f}"
    
    # Forecasting Table
    forecast_row = len(flights_list) + 11
    ws[f"A{forecast_row}"] = "FORECASTING"
    ws[f"A{forecast_row}"].font = Font(bold=True, size=11, color="0078D4")
    
    forecast_row += 1
    forecast_headers = ["Metric", "Value"]
    for col, header in enumerate(forecast_headers, 1):
        cell = ws.cell(row=forecast_row, column=col)
        cell.value = header
        cell.fill = subheader_fill
        cell.font = subheader_font
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    forecast_row += 1
    total_impressions = sum(f.get("volume", 0) for f in flights_list)
    
    forecast_data = [
        ("Total Budget", f"{total_budget:,.2f} {currency_sym}"),
        ("CPM", f"{cpm_rate:,.2f} {currency_sym}"),
        ("Total Impressions", f"{total_impressions:,.0f}"),
        ("Est. Daily Impressions", f"{total_impressions / max(1, sum((f.get('end_date') - f.get('start_date')).days + 1 for f in flights_list) if flights_list and hasattr(flights_list[0].get('start_date'), '__sub__') else 1):,.0f}"),
    ]
    
    for metric, value in forecast_data:
        ws.cell(row=forecast_row, column=1).value = metric
        ws.cell(row=forecast_row, column=1).font = Font(bold=True)
        ws.cell(row=forecast_row, column=2).value = value
        forecast_row += 1
    
    # Set column widths
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    
    return wb

def create_pdf_export(flights_list, campaign_info, delivery_pressure_label, product_config, cpm_rate, currency_sym):
    """Create IO PDF file with same information as Excel."""
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=20,
        alignment=1  # center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    # Title
    elements.append(Paragraph("MEDIA PLAN - MONETIZE GUARANTEED", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Campaign Details
    campaign_data = [
        ["Advertiser:", campaign_info.get("advertiser", ""), "Market:", campaign_info.get("market", "")],
        ["Campaign:", campaign_info.get("campaign", ""), "Publisher:", campaign_info.get("publisher", "")],
        ["Order Type:", "Insertion Order", "Request Date:", datetime.now().strftime("%m/%d/%Y")],
    ]
    
    campaign_table = Table(campaign_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    campaign_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D9E1F2')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#D9E1F2')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(campaign_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Campaign Overview
    elements.append(Paragraph("CAMPAIGN OVERVIEW", heading_style))
    
    overview_data = [["Flight", "Product", "Start Date", "End Date", "Budget"]]
    total_budget = 0
    
    for flight in flights_list:
        flight_budget = flight.get('budget', 0)
        total_budget += flight_budget
        
        start_date = flight.get("start_date")
        if hasattr(start_date, "strftime"):
            start_str = start_date.strftime("%m/%d/%Y")
        else:
            start_str = str(start_date)
        
        end_date = flight.get("end_date")
        if hasattr(end_date, "strftime"):
            end_str = end_date.strftime("%m/%d/%Y")
        else:
            end_str = str(end_date)
        
        overview_data.append([
            str(flight.get("flight_num", 1)),
            flight.get("product", ""),
            start_str,
            end_str,
            f"{flight_budget:,.2f}"
        ])
    
    overview_data.append(["", "", "", "TOTAL:", f"{total_budget:,.2f} {currency_sym}"])
    
    overview_table = Table(overview_data, colWidths=[0.8*inch, 1.5*inch, 1.3*inch, 1.3*inch, 1.3*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(overview_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Forecasting
    elements.append(Paragraph("FORECASTING", heading_style))
    
    total_impressions = sum(f.get("volume", 0) for f in flights_list)
    flight_days = sum((f.get('end_date') - f.get('start_date')).days + 1 for f in flights_list if hasattr(f.get('start_date'), '__sub__')) if flights_list else 1
    
    forecast_data = [
        ["Total Budget", f"{total_budget:,.2f} {currency_sym}"],
        ["CPM", f"{cpm_rate:,.2f} {currency_sym}"],
        ["Total Impressions", f"{total_impressions:,.0f}"],
        ["Est. Daily Impressions", f"{total_impressions / max(1, flight_days):,.0f}"],
    ]
    
    forecast_table = Table(forecast_data, colWidths=[2.5*inch, 2.5*inch])
    forecast_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D9E1F2')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(forecast_table)
    
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

# ================================================================================
# 2. CAMPAIGN DETAILS (INPUTS)
# ================================================================================
st.markdown("## Campaign Details")
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

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
st.markdown("## O&O Naming Taxonomy")
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

taxonomy = generate_o_o_taxonomy(market, publisher, product, ad_format, device)
li_name = generate_li_name(advertiser or "ADVERTISER", market, publisher, product)

col_tax1, col_tax2 = st.columns(2)

with col_tax1:
    st.markdown("**O&O Taxonomy**")
    st.code(taxonomy, language="text")

with col_tax2:
    st.markdown("**Line Item Name**")
    st.code(li_name, language="text")

# ================================================================================
# 4. PRICING
# ================================================================================
st.markdown("## Pricing")
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

currency_sym = get_currency_symbol(market)
currency_code = REGION_CURRENCY.get(market.upper(), ("USD", "$"))[0]

st.markdown("**Forecasting:** Impressions = (Spend ÷ CPM) × 1,000")

col_price1, col_price2, col_price3 = st.columns(3)

with col_price1:
    budget = st.number_input(
        f"Budget/Spend ({currency_sym})",
        min_value=0.0,
        value=1000.0,
        step=0.01,
        key="budget_value"
    )

with col_price2:
    cpm_rate = st.number_input(
        f"CPM ({currency_sym})",
        min_value=0.01,
        value=10.0,
        step=0.01,
        key="cpm_rate"
    )

with col_price3:
    if cpm_rate > 0:
        impressions = (budget / cpm_rate) * 1000
        st.metric("Calculated Impressions", f"{impressions:,.0f}")
    else:
        impressions = 0
        st.metric("Calculated Impressions", "0")

total_cost = budget

st.caption(f"💡 CPM rate ({currency_sym}{cpm_rate:.2f}) should align with DNV Rate Card for {market}. Confirm before IO submission.")

# ================================================================================
# 5. TARGETING RULES (LOCKED BY PRODUCT)
# ================================================================================
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
st.markdown("## Targeting Rules")

product_config = PRODUCT_RULES.get(product, {})

st.markdown("**Product Configuration** _(Locked by product)_")

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
st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
st.markdown("## Monetize Setup")

product_rule_str = f"Seat 280 • {product_config.get('line_item_type', 'PG')} • Priority {product_config.get('priority', '-')} • Pacing: {product_config.get('pacing', 'Even')} • Freq Cap: {product_config.get('frequency_cap', 'N/A')} • Publisher: {product_config.get('publisher_targeting', 'N/A')} • Format: {ad_format} • Location: {market}"
st.info(product_rule_str)

# ================================================================================
# 7. MANAGE MULTIPLE FLIGHTS
# ================================================================================
st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
st.markdown("## Multiple Flights")

st.write(f"**Current Flights:** {len(st.session_state.flights)}")

if st.button("➕ Add New Flight (Same Product, Different Dates & Budget)", use_container_width=True):
    new_flight = {
        "flight_num": len(st.session_state.flights) + 1,
        "product": product,
        "format": ad_format,
        "device": device,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "cpm": cpm_rate,
        "volume": impressions,
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
# PREPARE EXPORT DATA
# ================================================================================
# Define export_flights early so it can be used in Risk & Quality Control section
export_flights = st.session_state.flights if st.session_state.flights else [
    {
        "flight_num": 1,
        "product": product,
        "format": ad_format,
        "device": device,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "cpm": cpm_rate,
        "volume": impressions,
        "currency": currency_sym,
        "total_cost": total_cost
    }
]

# ================================================================================
# RISK & QUALITY CONTROL
# ================================================================================
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
st.markdown("## Risk & Quality Control")

product_config = PRODUCT_RULES.get(product, {})
freq_cap_text = product_config.get("frequency_cap", "6 impressions per user per day")
delivery_pressure, pressure_explanation = calculate_delivery_pressure(
    st.session_state.flights if st.session_state.flights else export_flights,
    product,
    freq_cap_text
)

# Calculate QC metrics
total_imp = sum(f.get("volume", 0) for f in (st.session_state.flights if st.session_state.flights else export_flights))
first_flight = (st.session_state.flights if st.session_state.flights else export_flights)[0] if (st.session_state.flights or export_flights) else {}
start_dt = first_flight.get("start_date")
end_dt = first_flight.get("end_date")
if isinstance(start_dt, str):
    from datetime import datetime
    start_dt = datetime.strptime(start_dt, "%Y-%m-%d").date()
if isinstance(end_dt, str):
    from datetime import datetime
    end_dt = datetime.strptime(end_dt, "%Y-%m-%d").date()
flight_duration = (end_dt - start_dt).days + 1 if start_dt and end_dt else 0

# Create unified checklist table combining TARGETING SETUP + QC CHECKLIST
unified_checklist = [
    ("Priority", product_config.get("priority", "N/A")),
    ("Frequency Cap", product_config.get("frequency_cap", "N/A")),
    ("Pacing", product_config.get("pacing", "Even")),
    ("KV Parameters", "KV pub=msn (MSN)" if publisher == "MSN" else "Direct Inventory (Outlook)" if publisher == "Outlook" else "KV pub=msn (MSN) | Direct (Outlook)"),
    ("Line Item Type", product_config.get("line_item_type", "N/A")),
    ("Dates", f"{start_dt.strftime('%m/%d/%Y') if start_dt else 'N/A'} - {end_dt.strftime('%m/%d/%Y') if end_dt else 'N/A'}"),
    ("Geo Targeting", product_config.get("geo_targeting", "Country required")),
    ("Delivery Risk Level", delivery_pressure),
    ("Total Flights", len(st.session_state.flights if st.session_state.flights else export_flights)),
    ("Flight Duration (days)", flight_duration),
    ("Est. Daily Impressions", f"{total_imp/flight_duration:,.0f}" if flight_duration > 0 else "0"),
    ("Total Impressions", f"{total_imp:,.0f}"),
    ("CPM", f"{cpm_rate:.2f} {currency_sym}"),
    ("Publisher Targeting", "KV" if publisher == "MSN" else "Direct Inventory"),
    ("Request Date", datetime.now().strftime("%m/%d/%Y")),
]

# Display unified table
table_data = []
for item_name, item_value in unified_checklist:
    table_data.append([item_name, str(item_value)])

df = pd.DataFrame(table_data, columns=["Item", "Value"])
st.dataframe(
    df, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Item": st.column_config.TextColumn(width="medium"),
        "Value": st.column_config.TextColumn(width="large"),
    }
)
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

# ================================================================================
# EXPORT MEDIA PLAN
# ================================================================================
st.markdown("## Export Media Plan")
st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

st.write("Download your media plan for client proposal in your preferred format:")
st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)

col_export1, col_export2, col_export3 = st.columns(3)

# IO Excel Export
with col_export1:
    excel_file = create_excel_export(
        export_flights, 
        st.session_state.campaign_details,
        delivery_pressure,
        product_config,
        cpm_rate,
        currency_sym
    )
    excel_bytes = BytesIO()
    excel_file.save(excel_bytes)
    excel_bytes.seek(0)
    
    st.download_button(
        label="📊 IO (Excel)",
        data=excel_bytes.getvalue(),
        file_name="MediaPlan_IO.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        help="Microsoft-style Excel file with campaign details and forecasting"
    )

# IO PDF Export
with col_export2:
    pdf_buffer = create_pdf_export(
        export_flights, 
        st.session_state.campaign_details,
        delivery_pressure,
        product_config,
        cpm_rate,
        currency_sym
    )
    
    st.download_button(
        label="📄 IO (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="MediaPlan_IO.pdf",
        mime="application/pdf",
        use_container_width=True,
        help="PDF version of the media plan"
    )

# Internal-Facing Excel Export
with col_export3:
    # Create internal-facing Excel with targeting setup
    internal_file = create_internal_excel_export(export_flights, st.session_state.campaign_details, delivery_pressure)
    internal_bytes = BytesIO()
    internal_file.save(internal_bytes)
    internal_bytes.seek(0)
    
    st.download_button(
        label="🔒 Internal Setup (Excel)",
        data=internal_bytes.getvalue(),
        file_name="MediaPlan_InternalSetup.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        help="Internal-facing Excel with targeting setup and QC checklist"
    )

st.divider()

st.markdown(f"""
<p style='text-align: center; font-size: 0.85rem; color: #666;'>
Monetize Guaranteed Media Planner • Seat 280 • Generated {datetime.now().strftime('%b %d, %Y at %I:%M %p')}
</p>
""", unsafe_allow_html=True)
