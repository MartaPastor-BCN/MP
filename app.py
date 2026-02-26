import streamlit as st
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import json
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Set page config
st.set_page_config(
    page_title="Monetize Media Planning",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.main { padding: 2rem 1rem; }
.stButton > button { width: 100%; }
h1 { color: #0078D4; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "num_flights" not in st.session_state:
    st.session_state.num_flights = 1

# Product rules for Monetize Seat 280
PRODUCTS = {
    "Programmatic Guaranteed - First Impression": {
        "formats": ["Banner"],
        "priority": 7
    },
    "Programmatic Guaranteed - Standard": {
        "formats": ["Banner", "Native"],
        "priority": 5
    },
    "GDALI - Guaranteed Campaign (Impressions)": {
        "formats": ["Banner", "Native", "Video"],
        "priority": 5
    },
    "GDALI - Takeover (MSN Homepage)": {
        "formats": ["Banner"],
        "priority": 15
    },
    "GDALI - Takeover (Outlook Native)": {
        "formats": ["Native"],
        "priority": 15
    },
    "PG - High Impact": {
        "formats": ["Banner"],
        "priority": 15
    }
}

DEVICE_MAPPING = {
    "Desktop": "D",
    "Mobile": "M",
    "Tablet": "T"
}

CURRENCY_MAP = {
    "US": "$", "CA": "$", "UK": "£", "DE": "€", "FR": "€", 
    "NL": "€", "ES": "€", "IT": "€", "AU": "$", "NZ": "$", 
    "SG": "$", "IN": "₹", "JP": "¥"
}

# Helper functions
def get_currency(market):
    return CURRENCY_MAP.get(market, "$")

def get_targeting(pub, prod):
    """Dynamic targeting based on publisher"""
    if pub == "Outlook":
        return "Direct Inventory"
    else:
        return "KV pub=msn"

def gen_taxonomy(advertiser, market, pub, fmt):
    """Generate taxonomy with advertiser"""
    return f"{advertiser}_{market}_{pub}_{fmt}"

def gen_li_name(advertiser, market, pub, fmt, device):
    """Line item naming convention"""
    device_code = DEVICE_MAPPING.get(device, "D")
    return f"{advertiser}_{market}_{pub}_{fmt}_{device_code}"

def calc_days(start, end):
    """Calculate days between dates"""
    return (end - start).days + 1

def calc_cost(vol, rate, is_cpd, days=1):
    """Calculate cost without discounts"""
    if is_cpd:
        return days * rate
    else:
        return (vol / 1000) * rate

def make_excel(flights_list, campaign_info):
    """Create Microsoft Advertising style Excel"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Campaign"
    
    # Set up formatting
    header_fill = PatternFill(start_color="0078D4", end_color="0078D4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Title section
    ws.merge_cells("A1:H1")
    title_cell = ws["A1"]
    title_cell.value = "Microsoft Advertising Campaign"
    title_cell.font = Font(bold=True, size=14, color="0078D4")
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    
    # Campaign info section
    ws["A2"] = "Campaign Name"
    ws["B2"] = campaign_info["campaign"]
    ws["A3"] = "Advertiser"
    ws["B3"] = campaign_info["advertiser"]
    ws["A4"] = "Market"
    ws["B4"] = campaign_info["market"]
    ws["C4"] = "Publisher"
    ws["D4"] = campaign_info["publisher"]
    
    # Data headers
    headers = ["Flight #", "Product", "Format", "Device", "Inventory", "Start Date", 
               "End Date", "Volume/Budget", "Rate", "Currency", "Cost"]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    
    # Data rows
    for row_idx, flight in enumerate(flights_list, 6):
        ws.cell(row=row_idx, column=1).value = flight.get("flight_num", 1)
        ws.cell(row=row_idx, column=2).value = flight["product"]
        ws.cell(row=row_idx, column=3).value = flight["format"]
        ws.cell(row=row_idx, column=4).value = flight["device"]
        ws.cell(row=row_idx, column=5).value = flight["inventory"]
        ws.cell(row=row_idx, column=6).value = flight["start"].strftime("%m/%d/%Y")
        ws.cell(row=row_idx, column=7).value = flight["end"].strftime("%m/%d/%Y")
        ws.cell(row=row_idx, column=8).value = flight["volume"]
        ws.cell(row=row_idx, column=9).value = flight["rate"]
        ws.cell(row=row_idx, column=10).value = flight["currency"]
        ws.cell(row=row_idx, column=11).value = flight["cost"]
        
        for col in range(1, 12):
            ws.cell(row=row_idx, column=col).border = border
    
    # Freeze panes
    ws.freeze_panes = "A5"
    
    # Set column widths
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 20
    ws.column_dimensions["F"].width = 12
    ws.column_dimensions["G"].width = 12
    ws.column_dimensions["H"].width = 15
    ws.column_dimensions["I"].width = 10
    ws.column_dimensions["J"].width = 12
    ws.column_dimensions["K"].width = 12
    
    return wb

def make_pdf(flights_list, campaign_info):
    """Create comprehensive PDF report with all 8 sections"""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    # ========== SECTION 1: HEADER / VERSIONING ==========
    story.append(Paragraph("Monetize Guaranteed Media Planning", title_style))
    story.append(Paragraph("Version 2.0 – MONETIZE SEAT 280 ONLY", styles['Normal']))
    story.append(Paragraph("<b>⚠️ CPM rates must be aligned with DNV Rate Card</b>", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 2: CAMPAIGN DETAILS ==========
    story.append(Paragraph("1. Campaign Details", heading_style))
    campaign_data = [
        ["Market", campaign_info["market"], "Advertiser", campaign_info["advertiser"]],
        ["Campaign", campaign_info["campaign"], "Publisher", campaign_info["publisher"]],
        ["Device", flights_list[0]["device"] if flights_list else "N/A", "Format", flights_list[0]["format"] if flights_list else "N/A"],
        ["Start Date", flights_list[0]["start"].strftime("%Y-%m-%d") if flights_list else "N/A", 
         "End Date", flights_list[-1]["end"].strftime("%Y-%m-%d") if flights_list else "N/A"]
    ]
    campaign_table = Table(campaign_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    campaign_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F0F0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(campaign_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 3: O&O NAMING TAXONOMY ==========
    story.append(Paragraph("2. O&O Naming Taxonomy", heading_style))
    if flights_list:
        flight = flights_list[0]
        taxonomy = f"{campaign_info['advertiser']}_{campaign_info['market']}_{campaign_info['publisher']}_{flight['format']}"
        line_item = f"{campaign_info['advertiser']}_{campaign_info['market']}_{campaign_info['publisher']}_{flight['format']}_{DEVICE_MAPPING.get(flight['device'], 'D')}"
        taxonomy_data = [
            ["Taxonomy", taxonomy],
            ["Line Item Name", line_item]
        ]
        taxonomy_table = Table(taxonomy_data, colWidths=[2*inch, 4.5*inch])
        taxonomy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(taxonomy_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 4: PRICING ==========
    story.append(Paragraph("3. Pricing & Booking Math", heading_style))
    if flights_list:
        flight = flights_list[0]
        pricing_data = [
            ["Rate Type", "CPM" if "CPM" in flight["rate_type"] else "CPD"],
            ["Rate", f"{flight['currency']}{flight['rate']:.2f}"],
            ["Impressions/Days", f"{flight['volume']:,}"],
            ["Total Cost", f"{flight['currency']}{flight['cost']:,.2f}"]
        ]
        pricing_table = Table(pricing_data, colWidths=[2*inch, 2*inch])
        pricing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(pricing_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 5: TARGETING RULES ==========
    story.append(Paragraph("4. Targeting Rules (Product-Locked)", heading_style))
    if flights_list:
        flight = flights_list[0]
        targeting_data = [
            ["Seat", "280 - Monetize"],
            ["Priority", str(PRODUCTS.get(flight['product'], {}).get('priority', 'N/A'))],
            ["Frequency Cap", "1/day" if "First Impression" in flight['product'] else "6/day"],
            ["Pacing", "ASAP" if "First Impression" in flight['product'] else "Even"],
            ["Inventory Type", flight["inventory"]],
            ["Geo Targeting", "Country required"],
            ["Publisher Targeting", "KV pub=msn" if "MSN" in campaign_info['publisher'] else "Direct Inventory"],
            ["Revenue Type", flight["rate_type"].split("(")[0].strip()]
        ]
        targeting_table = Table(targeting_data, colWidths=[2.5*inch, 3.5*inch])
        targeting_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(targeting_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 6: MONETIZE SETUP CHECKLIST ==========
    story.append(PageBreak())
    story.append(Paragraph("5. Monetize Setup Summary", heading_style))
    if flights_list:
        flight = flights_list[0]
        setup_text = f"<b>✓ Seat 280</b> | <b>✓ PG</b> | <b>✓ Priority {PRODUCTS.get(flight['product'], {}).get('priority', 'N/A')}</b> | <b>✓ {flight['format']}</b> | <b>✓ Country Geo</b> | <b>✓ {campaign_info['publisher']} Inventory</b>"
        story.append(Paragraph(setup_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 7: MULTIPLE FLIGHTS ==========
    story.append(Paragraph("6. Media Plan (Flights)", heading_style))
    if flights_list:
        flight_headers = ["Flight", "Product", "Format", "Start", "End", "Volume", "Rate", "Cost"]
        flight_rows = []
        for idx, flight in enumerate(flights_list, 1):
            flight_rows.append([
                str(idx),
                flight['product'][:20] + "..." if len(flight['product']) > 20 else flight['product'],
                flight['format'],
                flight['start'].strftime("%m/%d"),
                flight['end'].strftime("%m/%d"),
                f"{flight['volume']:,}",
                f"{flight['currency']}{flight['rate']:.2f}",
                f"{flight['currency']}{flight['cost']:,.2f}"
            ])
        flight_data = [flight_headers] + flight_rows
        flight_table = Table(flight_data, colWidths=[0.6*inch, 2*inch, 0.9*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch, 1*inch])
        flight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(flight_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 8: EXPORT FOOTER ==========
    story.append(Paragraph("7. Summary & Export", heading_style))
    if flights_list:
        total_cost = sum(f['cost'] for f in flights_list)
        total_volume = sum(f['volume'] for f in flights_list)
        currency = flights_list[0]['currency']
        summary_data = [
            ["Total Flights", str(len(flights_list))],
            ["Total Impressions", f"{total_volume:,}"],
            ["Total Cost", f"{currency}{total_cost:,.2f}"],
            ["Avg CPM", f"{currency}{(total_cost/total_volume*1000) if total_volume > 0 else 0:.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0078D4')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(summary_table)
    
    story.append(Spacer(1, 0.3*inch))
    footer = f"<b>Monetize Seat 280 – Guaranteed Delivery Only</b><br/>Last Updated: {datetime.now().strftime('%B %d, %Y')}<br/>✓ CPM rates aligned with DNV Rate Card"
    story.append(Paragraph(footer, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

# Main UI
st.title("📊 Microsoft Advertising Monetize Media Planning")
st.markdown("**Seat 280 - Guaranteed Media Planner**")
st.divider()

# Campaign section
col1, col2, col3, col4 = st.columns(4)
with col1:
    advertiser = st.text_input("Advertiser", help="Campaign advertiser")
with col2:
    campaign = st.text_input("Campaign Name", help="Campaign identifier")
with col3:
    market = st.selectbox("Market", list(CURRENCY_MAP.keys()), help="Target market")
with col4:
    publisher = st.selectbox("Publisher", ["Outlook", "MSN"], help="Publisher selection")

st.divider()

# Product & Format section
col1, col2, col3, col4 = st.columns(4)
with col1:
    product = st.selectbox("Product", list(PRODUCTS.keys()), help="Guaranteed product type")
with col2:
    available_formats = PRODUCTS[product]["formats"]
    format_select = st.selectbox("Format/Inventory", available_formats, help="Creative format")
with col3:
    device = st.selectbox("Device", list(DEVICE_MAPPING.keys()), help="Target device")
with col4:
    currency = get_currency(market)
    st.metric("Currency", currency)

# Show dynamic targeting
col1, col2 = st.columns(2)
with col1:
    targeting = get_targeting(publisher, product)
    st.info(f"**Inventory Type:** {targeting}")

st.divider()

# Flights section
col1, col2 = st.columns(2)
with col1:
    multi_flight = st.checkbox("Add Multiple Flights", value=False, help="Enable multi-flight planning")

if multi_flight:
    st.session_state.num_flights = st.number_input("Number of Flights", min_value=1, max_value=12, value=1)
else:
    st.session_state.num_flights = 1

st.divider()

flights_data = []

for flight_num in range(1, st.session_state.num_flights + 1):
    st.markdown(f"**Flight {flight_num}**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        start_date = st.date_input(f"Start Date", key=f"start_{flight_num}")
    with col2:
        end_date = st.date_input(f"End Date", key=f"end_{flight_num}")
    with col3:
        rate = st.number_input(f"Rate ({currency})", min_value=0.0, value=10.0, key=f"rate_{flight_num}")
    with col4:
        volume = st.number_input(f"Volume/Impressions", min_value=0, value=100000, key=f"volume_{flight_num}")
    with col5:
        rate_type = st.selectbox("Type", ["CPM (Cost per 1K)", "CPD (Cost per Day)"], key=f"type_{flight_num}")
    
    is_cpd = "CPD" in rate_type
    days = calc_days(start_date, end_date)
    cost = calc_cost(volume, rate, is_cpd, days)
    
    flights_data.append({
        "flight_num": flight_num,
        "product": product,
        "format": format_select,
        "device": device,
        "inventory": get_targeting(publisher, product),
        "start": start_date,
        "end": end_date,
        "volume": volume,
        "rate": rate,
        "currency": currency,
        "cost": cost,
        "days": days,
        "rate_type": rate_type
    })
    
    st.caption(f"Duration: {days} days | Cost: {currency}{cost:,.2f}")
    st.divider()

# Summary and export
if advertiser and campaign and flights_data:
    total_cost = sum(f["cost"] for f in flights_data)
    total_volume = sum(f["volume"] for f in flights_data)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Flights", len(flights_data))
    with col2:
        st.metric("Total Volume", f"{total_volume:,}")
    with col3:
        st.metric("Total Cost", f"{currency}{total_cost:,.2f}")
    with col4:
        st.metric("Avg Rate", f"{currency}{(total_cost/total_volume*1000) if total_volume > 0 else 0:.2f}/K")
    
    st.divider()
    
    # Export section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        campaign_info = {
            "advertiser": advertiser,
            "campaign": campaign,
            "market": market,
            "publisher": publisher
        }
        
        wb = make_excel(flights_data, campaign_info)
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        filename = f"{advertiser}_{campaign}_{market}_{publisher}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        campaign_info = {
            "advertiser": advertiser,
            "campaign": campaign,
            "market": market,
            "publisher": publisher
        }
        
        pdf_buffer = make_pdf(flights_data, campaign_info)
        pdf_filename = f"Monetize_Media_Plan_{advertiser}_{campaign}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )
    
    with col3:
        json_data = {
            "campaign_info": {
                "advertiser": advertiser,
                "campaign": campaign,
                "market": market,
                "publisher": publisher
            },
            "flights": flights_data
        }
        
        json_filename = f"{advertiser}_{campaign}_{market}_{publisher}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(json_data, indent=2, default=str),
            file_name=json_filename,
            mime="application/json",
            use_container_width=True
        )
else:
    st.warning("⚠️ Fill in Campaign Name and Advertiser to generate exports")
