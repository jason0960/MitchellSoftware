"""
Lumber Yard Restock Planner — Flask PDF Server
Generates incoming delivery restock order PDFs with ReportLab.
"""
import io
import base64
import json
from datetime import datetime

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


@app.route('/')
def index():
    return app.send_static_file('pallet-builder.html')

HD_ORANGE = colors.HexColor('#F96302')
DARK_BG   = colors.HexColor('#0a0e17')
CARD_BG   = colors.HexColor('#1a2233')
BORDER    = colors.HexColor('#1e293b')
TEXT      = colors.HexColor('#e2e8f0')
MUTED     = colors.HexColor('#94a3b8')
GREEN     = colors.HexColor('#22c55e')
RED       = colors.HexColor('#ef4444')
YELLOW    = colors.HexColor('#eab308')


def get_fill_color(pct):
    if pct >= 0.8:
        return GREEN
    if pct >= 0.5:
        return colors.HexColor('#86efac')
    if pct >= 0.2:
        return YELLOW
    if pct > 0:
        return RED
    return colors.HexColor('#374151')


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    items = data.get('items', [])
    truck_image = data.get('truckImage', '')
    chart_image = data.get('chartImage', '')
    total_weight = data.get('totalWeight', 0)
    total_cost = data.get('totalCost', 0)
    total_pieces = data.get('totalPieces', 0)
    total_bunks = data.get('totalBunks', 0)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'HDTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=20,
        textColor=HD_ORANGE, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'HDSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10,
        textColor=MUTED, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        'SectionHead', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=13,
        textColor=HD_ORANGE, spaceBefore=14, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'CellText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5,
        textColor=colors.black,
    ))
    styles.add(ParagraphStyle(
        'CellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5,
        textColor=colors.black,
    ))
    styles.add(ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7,
        textColor=MUTED, alignment=TA_CENTER,
    ))

    elems = []

    # ── HEADER ──
    now = datetime.now()
    elems.append(Paragraph('LUMBER YARD RESTOCK ORDER', styles['HDTitle']))
    elems.append(Paragraph(
        f'Generated: {now.strftime("%B %d, %Y at %I:%M %p")} &nbsp;|&nbsp; '
        f'Order #{now.strftime("%y%m%d")}-{total_bunks:02d}',
        styles['HDSub'],
    ))
    elems.append(HRFlowable(
        width='100%', thickness=2, color=HD_ORANGE,
        spaceAfter=10, spaceBefore=2,
    ))

    # ── SUMMARY BOX ──
    summary_data = [
        ['RESTOCK SUMMARY', '', '', ''],
        ['Bunks to Restock', 'Total Pieces', 'Total Weight', 'Estimated Cost'],
        [str(total_bunks), f'{total_pieces:,}', f'{total_weight:,} lbs', f'${total_cost:,.2f}'],
    ]
    summary_table = Table(summary_data, colWidths=[doc.width / 4] * 4)
    summary_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), HD_ORANGE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 8),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#666666')),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 14),
        ('TEXTCOLOR', (0, 2), (-1, 2), HD_ORANGE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, HD_ORANGE),
        ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 2), (-1, 2), 8),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
    ]))
    elems.append(summary_table)
    elems.append(Spacer(1, 14))

    # ── LINE ITEMS TABLE ──
    elems.append(Paragraph('ORDER LINE ITEMS', styles['SectionHead']))

    header = ['#', 'Product', 'Category', 'In Stock', 'Capacity', 'Order Qty',
              'Unit $/pc', 'Weight/pc', 'Line Total']
    table_data = [header]

    for i, item in enumerate(items, 1):
        pct = item['current'] / item['capacity'] if item['capacity'] > 0 else 0
        table_data.append([
            str(i),
            item['name'],
            item['category'],
            str(item['current']),
            str(item['capacity']),
            str(item['toOrder']),
            f"${item['unitPrice']:.2f}",
            f"{item['unitWeight']} lbs",
            f"${item['totalCost']:,.2f}",
        ])

    # Totals row
    table_data.append([
        '', '', '', '', '', str(total_pieces),
        '', f'{total_weight:,} lbs', f'${total_cost:,.2f}',
    ])

    col_widths = [0.3*inch, 1.3*inch, 0.8*inch, 0.6*inch, 0.6*inch,
                  0.65*inch, 0.65*inch, 0.7*inch, 0.85*inch]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HD_ORANGE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (0, 0), (-1, -1), 1, HD_ORANGE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fafafa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        # Totals row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fff3e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), HD_ORANGE),
        ('LINEABOVE', (0, -1), (-1, -1), 2, HD_ORANGE),
    ]

    # Color-code stock cells
    for i, item in enumerate(items, 1):
        pct = item['current'] / item['capacity'] if item['capacity'] > 0 else 0
        c = get_fill_color(pct)
        style_cmds.append(('TEXTCOLOR', (3, i), (3, i), c))

    t.setStyle(TableStyle(style_cmds))
    elems.append(t)
    elems.append(Spacer(1, 12))

    # ── TRUCK DIAGRAM ──
    if truck_image:
        elems.append(PageBreak())
        elems.append(Paragraph('FLATBED DELIVERY — LOADING PLAN', styles['SectionHead']))
        try:
            img_data = base64.b64decode(truck_image.split(',')[1])
            img_buf = io.BytesIO(img_data)
            img = Image(img_buf, width=7.4 * inch, height=4.3 * inch)
            elems.append(img)
        except Exception as e:
            elems.append(Paragraph(f'[Truck diagram error: {e}]', styles['Normal']))
        elems.append(Spacer(1, 14))

    # ── YARD CHART ──
    if chart_image:
        elems.append(Paragraph('YARD INVENTORY STATUS', styles['SectionHead']))
        try:
            img_data = base64.b64decode(chart_image.split(',')[1])
            img_buf = io.BytesIO(img_data)
            img = Image(img_buf, width=6.8 * inch, height=2 * inch)
            elems.append(img)
        except Exception as e:
            elems.append(Paragraph(f'[Chart error: {e}]', styles['Normal']))
        elems.append(Spacer(1, 14))

    # ── FOOTER ──
    elems.append(HRFlowable(
        width='100%', thickness=1, color=MUTED,
        spaceAfter=6, spaceBefore=6,
    ))
    elems.append(Paragraph(
        'Generated by Lumber Yard Restock Planner — Jason Mitchell | '
        'mitchellsoftware.dev &nbsp;|&nbsp; Powered by Three.js + ReportLab',
        styles['Footer'],
    ))

    doc.build(elems)
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f'restock-order-{now.strftime("%Y%m%d")}.pdf',
    )


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'Lumber Yard Restock Planner'})


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print('\n🪵  Lumber Yard Restock Planner — PDF Server')
    print(f'   http://localhost:{port}\n')
    app.run(debug=debug, host='0.0.0.0', port=port)
