"""
Lumber Yard Restock Planner — Flask PDF Server
Generates incoming delivery restock order PDFs with ReportLab.
Exposes Prometheus /metrics endpoint for observability.
"""
import io
import base64
import json
import time
import os
import sqlite3
import uuid
import psutil
from datetime import datetime
from openai import OpenAI

from flask import Flask, request, send_file, jsonify, Response
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
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/metrics": {"origins": "*"}, r"/admin/*": {"origins": "*"}})

SERVER_START_TIME = time.time()

# ─── Prometheus Counters ───────────────────────────────────────
PORTFOLIO_VIEWS = Counter(
    'portfolio_page_views_total',
    'Total views of the main portfolio page'
)
DEMO_VIEWS = Counter(
    'demo_page_views_total',
    'Total views of the Lumber Yard Restock Planner demo'
)
PDF_GENERATIONS = Counter(
    'pdf_generations_total',
    'Total PDF restock orders generated'
)
CONTACT_SUBMISSIONS = Counter(
    'contact_form_submissions_total',
    'Total contact form submissions'
)
RESUME_ENJOYED = Counter(
    'resume_enjoyed_votes_total',
    'Total \"Enjoyed this resume\" votes'
)
CHAT_MESSAGES = Counter(
    'chat_messages_total',
    'Total AI chatbot messages received'
)
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# ─── Prometheus Gauges (system health) ─────────────────────────
UPTIME_GAUGE = Gauge(
    'server_uptime_seconds',
    'Server uptime in seconds'
)
MEMORY_USAGE_MB = Gauge(
    'process_memory_usage_mb',
    'Process memory usage in MB'
)
CPU_PERCENT = Gauge(
    'process_cpu_percent',
    'Process CPU usage percentage'
)
ACTIVE_SESSIONS = Gauge(
    'active_sessions_current',
    'Estimated unique visitors in last 15 minutes'
)

# ─── Prometheus Histograms ─────────────────────────────────────
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

# ─── Session Tracking ──────────────────────────────────────────
# In-memory session tracking (visitor IPs seen in last 15 min)
_visitor_log = {}  # { ip: last_seen_timestamp }
SESSION_WINDOW = 900  # 15 minutes

# ─── SQLite Chat Log Database ──────────────────────────────────
CHAT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_logs.db')


def _init_chat_db():
    """Create the chat log tables if they don't exist."""
    conn = sqlite3.connect(CHAT_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            recruiter_name TEXT NOT NULL,
            job_posting TEXT,
            started_at TEXT NOT NULL,
            last_message_at TEXT NOT NULL,
            ip_address TEXT,
            message_count INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    conn.commit()
    conn.close()


_init_chat_db()


# ─── AI Chatbot System Prompt ──────────────────────────────────
def _load_system_prompt():
    """Load Jason's profile data and build the system prompt."""
    profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jason_profile.json')
    with open(profile_path, 'r') as f:
        profile = json.load(f)

    return f"""You are Jason Mitchell's AI representative on his portfolio website. Your job is to answer questions from recruiters and hiring managers about Jason's experience, skills, and background.

IMPORTANT RULES:
- Be honest and transparent. Never exaggerate or fabricate experience.
- If asked about something Jason doesn't have experience with, say so clearly but frame it constructively (e.g., "Jason hasn't worked with Kubernetes in production yet, but he's familiar with containerization concepts and is eager to learn.").
- Be conversational, professional, and warm — represent Jason well.
- Keep responses concise but thorough. Aim for 2-4 sentences unless more detail is requested.
- If a recruiter pastes a job posting, give an honest assessment of fit — highlight matching skills AND gaps.
- You may refer to Jason in the third person ("Jason has...") or first person ("I have...") — match whatever feels natural in context.
- Never make up specific dates, numbers, or claims not in the profile data.
- If asked something personal or inappropriate, politely decline.

JASON'S PROFILE DATA:
{json.dumps(profile, indent=2)}

Remember: honesty is Jason's differentiator. Recruiters appreciate candor over sales pitches."""


# Cache the system prompt at startup
try:
    SYSTEM_PROMPT = _load_system_prompt()
except Exception as e:
    print(f'Warning: Could not load profile for AI chatbot: {e}')
    SYSTEM_PROMPT = 'You are Jason Mitchell\'s AI assistant. Answer questions about his software engineering experience honestly.'

# OpenAI client (initialized lazily)
_openai_client = None


def _get_openai_client():
    """Get or create the OpenAI client."""
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OPENAI_API_KEY environment variable is not set')
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def _update_system_metrics():
    """Update system-level gauges."""
    UPTIME_GAUGE.set(time.time() - SERVER_START_TIME)
    process = psutil.Process(os.getpid())
    MEMORY_USAGE_MB.set(round(process.memory_info().rss / 1024 / 1024, 1))
    CPU_PERCENT.set(process.cpu_percent(interval=None))


def _track_visitor(ip):
    """Track unique visitors in a sliding window."""
    now = time.time()
    _visitor_log[ip] = now
    # Prune old entries
    cutoff = now - SESSION_WINDOW
    to_delete = [k for k, v in _visitor_log.items() if v < cutoff]
    for k in to_delete:
        del _visitor_log[k]
    ACTIVE_SESSIONS.set(len(_visitor_log))


@app.before_request
def before_request():
    request._start_time = time.time()
    _track_visitor(request.remote_addr or 'unknown')


@app.after_request
def after_request(response):
    latency = time.time() - getattr(request, '_start_time', time.time())
    endpoint = request.endpoint or 'unknown'
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    return response


@app.route('/metrics')
def metrics():
    _update_system_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/api/track', methods=['POST'])
def track_event():
    data = request.get_json(silent=True) or {}
    event = data.get('event', '')

    counter_map = {
        'portfolio_view': PORTFOLIO_VIEWS,
        'demo_view': DEMO_VIEWS,
        'pdf_generated': PDF_GENERATIONS,
        'contact_submit': CONTACT_SUBMISSIONS,
        'resume_enjoyed': RESUME_ENJOYED,
    }

    counter = counter_map.get(event)
    if counter:
        counter.inc()
        return jsonify({'ok': True, 'event': event})
    return jsonify({'ok': False, 'error': 'unknown event'}), 400


@app.route('/api/stats')
def get_stats():
    _update_system_metrics()
    uptime = time.time() - SERVER_START_TIME
    hours, rem = divmod(int(uptime), 3600)
    minutes, seconds = divmod(rem, 60)
    process = psutil.Process(os.getpid())
    return jsonify({
        'portfolio_views': int(PORTFOLIO_VIEWS._value.get()),
        'demo_views': int(DEMO_VIEWS._value.get()),
        'pdf_generations': int(PDF_GENERATIONS._value.get()),
        'contact_submissions': int(CONTACT_SUBMISSIONS._value.get()),
        'resume_enjoyed': int(RESUME_ENJOYED._value.get()),
        'health': {
            'uptime_seconds': round(uptime, 1),
            'uptime_display': f'{hours}h {minutes}m {seconds}s',
            'memory_mb': round(process.memory_info().rss / 1024 / 1024, 1),
            'cpu_percent': process.cpu_percent(interval=None),
            'active_sessions': len(_visitor_log),
        }
    })


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


# ─── AI Chatbot Endpoints ──────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle a chat message from a recruiter."""
    data = request.get_json(silent=True) or {}
    recruiter_name = data.get('recruiter_name', '').strip()
    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id', '')
    job_posting = data.get('job_posting', '')

    if not recruiter_name:
        return jsonify({'error': 'Please provide your name.'}), 400
    if not message:
        return jsonify({'error': 'Please provide a message.'}), 400

    now = datetime.utcnow().isoformat()
    ip = request.remote_addr or 'unknown'

    conn = sqlite3.connect(CHAT_DB_PATH)
    c = conn.cursor()

    # Create or retrieve conversation
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        c.execute(
            'INSERT INTO conversations (id, recruiter_name, job_posting, started_at, last_message_at, ip_address, message_count) VALUES (?, ?, ?, ?, ?, ?, 0)',
            (conversation_id, recruiter_name, job_posting, now, now, ip)
        )
    else:
        # Update existing conversation
        c.execute('UPDATE conversations SET last_message_at = ? WHERE id = ?', (now, conversation_id))
        # Update job posting if provided and conversation exists
        if job_posting:
            c.execute('UPDATE conversations SET job_posting = ? WHERE id = ?', (job_posting, conversation_id))

    # Save user message
    c.execute(
        'INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
        (conversation_id, 'user', message, now)
    )
    c.execute('UPDATE conversations SET message_count = message_count + 1 WHERE id = ?', (conversation_id,))
    conn.commit()

    CHAT_MESSAGES.inc()

    # Build conversation history for context
    c.execute(
        'SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id',
        (conversation_id,)
    )
    history = [{'role': row[0], 'content': row[1]} for row in c.fetchall()]

    # Build messages for LLM
    llm_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    # Inject job posting context if present
    if job_posting:
        llm_messages.append({
            'role': 'system',
            'content': f'The recruiter has shared this job posting for fit assessment:\n\n{job_posting}'
        })

    # Add recruiter name context
    llm_messages.append({
        'role': 'system',
        'content': f'The recruiter\'s name is {recruiter_name}. You may address them by name occasionally.'
    })

    llm_messages.extend([
        {'role': 'user' if m['role'] == 'user' else 'assistant', 'content': m['content']}
        for m in history
    ])

    # Call the LLM
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=llm_messages,
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
    except ValueError as e:
        conn.close()
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        conn.close()
        return jsonify({'error': f'AI service temporarily unavailable: {str(e)}'}), 503

    # Save assistant reply
    reply_time = datetime.utcnow().isoformat()
    c.execute(
        'INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
        (conversation_id, 'assistant', reply, reply_time)
    )
    c.execute('UPDATE conversations SET message_count = message_count + 1, last_message_at = ? WHERE id = ?',
              (reply_time, conversation_id))
    conn.commit()
    conn.close()

    return jsonify({
        'reply': reply,
        'conversation_id': conversation_id,
    })


# ─── Admin: View Chat Logs (token-protected) ──────────────────

@app.route('/admin/chat-logs')
def admin_chat_logs():
    """View all chat logs. Protected by ADMIN_TOKEN env var."""
    token = request.args.get('token', '')
    expected = os.environ.get('ADMIN_TOKEN', '')

    if not expected or token != expected:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(CHAT_DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM conversations ORDER BY last_message_at DESC')
    conversations = []
    for row in c.fetchall():
        conv = dict(row)
        c.execute(
            'SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id',
            (conv['id'],)
        )
        conv['messages'] = [dict(m) for m in c.fetchall()]
        conversations.append(conv)

    conn.close()

    return jsonify({
        'total_conversations': len(conversations),
        'conversations': conversations,
    })


@app.route('/admin/chat-stats')
def admin_chat_stats():
    """Quick stats overview. Protected by ADMIN_TOKEN."""
    token = request.args.get('token', '')
    expected = os.environ.get('ADMIN_TOKEN', '')

    if not expected or token != expected:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(CHAT_DB_PATH)
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM conversations')
    total_convos = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM messages')
    total_messages = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM messages WHERE role = "user"')
    total_user_messages = c.fetchone()[0]

    c.execute('SELECT recruiter_name, COUNT(*) as msg_count, started_at FROM conversations GROUP BY recruiter_name ORDER BY started_at DESC LIMIT 20')
    recent_recruiters = [{'name': r[0], 'conversations': r[1], 'first_seen': r[2]} for r in c.fetchall()]

    conn.close()

    return jsonify({
        'total_conversations': total_convos,
        'total_messages': total_messages,
        'total_user_messages': total_user_messages,
        'recent_recruiters': recent_recruiters,
    })


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
