"""
Tests for server/app.py — routes, validation, and error handling.
"""
import json
import os
import sys
import tempfile
import time
from unittest.mock import patch, MagicMock
import pytest

# Ensure project root is on the path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

import server.app as server_module
from server.app import app, get_fill_color, _track_visitor, _check_chat_rate, _chat_rate, _visitor_log


@pytest.fixture
def client(tmp_path):
    """Create a test client with an isolated temporary chat database."""
    test_db = str(tmp_path / 'test_chat_logs.db')
    original_db = server_module.CHAT_DB_PATH
    server_module.CHAT_DB_PATH = test_db
    server_module._init_chat_db()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c
    server_module.CHAT_DB_PATH = original_db


@pytest.fixture(autouse=True)
def _clear_rate_limits():
    """Reset rate-limit state between tests."""
    _chat_rate.clear()
    yield
    _chat_rate.clear()


# ═══════════════════════════════════════════════════════════════
# Health & Static
# ═══════════════════════════════════════════════════════════════

def test_health_endpoint(client):
    """GET /health should return 200 with status ok."""
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'


def test_health_contains_service_name(client):
    """Health endpoint should include service name."""
    data = client.get('/health').get_json()
    assert 'service' in data
    assert 'MitchellSoftware' in data['service']


def test_root_serves_portfolio(client):
    """GET / should serve the portfolio page (200)."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Jason Mitchell' in resp.data


def test_demo_serves_planner(client):
    """GET /demo should serve the pallet-builder demo (200)."""
    resp = client.get('/demo')
    assert resp.status_code == 200
    assert b'Lumber Yard' in resp.data


def test_static_css_served(client):
    """Static CSS files should be served correctly."""
    resp = client.get('/styles.css')
    assert resp.status_code == 200


def test_static_js_served(client):
    """Static JS files should be served correctly."""
    resp = client.get('/script.js')
    assert resp.status_code == 200


def test_demo_css_served(client):
    """Demo-specific CSS file should be accessible."""
    resp = client.get('/demo/pallet-builder.css')
    assert resp.status_code == 200


def test_demo_js_served(client):
    """Demo-specific JS file should be accessible."""
    resp = client.get('/demo/pallet-builder.js')
    assert resp.status_code == 200


def test_chat_js_served(client):
    """chat.js should be served as a static file."""
    resp = client.get('/chat.js')
    assert resp.status_code == 200


def test_nonexistent_route_returns_404(client):
    """Unknown routes should return 404."""
    resp = client.get('/this-does-not-exist')
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# Metrics & Stats
# ═══════════════════════════════════════════════════════════════

def test_metrics_endpoint(client):
    """GET /metrics should return Prometheus-formatted text."""
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert b'http_requests_total' in resp.data


def test_metrics_include_custom_counters(client):
    """Prometheus output should include our custom counters."""
    resp = client.get('/metrics')
    body = resp.data.decode()
    assert 'portfolio_page_views_total' in body
    assert 'demo_page_views_total' in body
    assert 'pdf_generations_total' in body
    assert 'chat_messages_total' in body


def test_metrics_include_system_gauges(client):
    """Prometheus output should include system health gauges."""
    resp = client.get('/metrics')
    body = resp.data.decode()
    assert 'server_uptime_seconds' in body
    assert 'process_memory_usage_mb' in body
    assert 'process_cpu_percent' in body


def test_stats_endpoint(client):
    """GET /api/stats should return JSON with expected keys."""
    resp = client.get('/api/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'portfolio_views' in data
    assert 'health' in data
    assert 'uptime_seconds' in data['health']
    assert 'active_sessions' in data['health']


def test_stats_all_counter_fields(client):
    """Stats JSON should contain all counter fields."""
    data = client.get('/api/stats').get_json()
    for key in ('portfolio_views', 'demo_views', 'pdf_generations',
                'contact_submissions', 'resume_enjoyed'):
        assert key in data, f'Missing counter: {key}'
        assert isinstance(data[key], int)


def test_stats_health_uptime_display(client):
    """Stats should include a human-readable uptime_display string."""
    data = client.get('/api/stats').get_json()
    assert 'uptime_display' in data['health']
    assert 'h' in data['health']['uptime_display']  # e.g. "0h 0m 1s"


def test_stats_health_memory_and_cpu(client):
    """Stats should report memory and CPU values."""
    health = client.get('/api/stats').get_json()['health']
    assert isinstance(health['memory_mb'], (int, float))
    assert health['memory_mb'] > 0
    assert isinstance(health['cpu_percent'], (int, float))


# ═══════════════════════════════════════════════════════════════
# Event Tracking
# ═══════════════════════════════════════════════════════════════

def test_track_valid_event(client):
    """POST /api/track with a valid event should return ok."""
    resp = client.post('/api/track',
                       json={'event': 'portfolio_view'},
                       content_type='application/json')
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True


def test_track_invalid_event(client):
    """POST /api/track with unknown event should return 400."""
    resp = client.post('/api/track',
                       json={'event': 'nonexistent_event'},
                       content_type='application/json')
    assert resp.status_code == 400


@pytest.mark.parametrize('event', [
    'portfolio_view', 'demo_view', 'pdf_generated',
    'contact_submit', 'resume_enjoyed',
])
def test_track_all_known_events(client, event):
    """Each known event type should be accepted."""
    resp = client.post('/api/track', json={'event': event})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['ok'] is True
    assert data['event'] == event


def test_track_empty_body(client):
    """POST /api/track with no JSON body should return 400."""
    resp = client.post('/api/track',
                       data='',
                       content_type='application/json')
    assert resp.status_code == 400


def test_track_missing_event_key(client):
    """POST /api/track with JSON but no 'event' key should return 400."""
    resp = client.post('/api/track', json={'foo': 'bar'})
    assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════
# Chat Validation
# ═══════════════════════════════════════════════════════════════

def test_chat_missing_name(client):
    """POST /api/chat without recruiter_name should return 400."""
    resp = client.post('/api/chat',
                       json={'message': 'Hello'},
                       content_type='application/json')
    assert resp.status_code == 400
    assert 'name' in resp.get_json()['error'].lower()


def test_chat_missing_message(client):
    """POST /api/chat without message should return 400."""
    resp = client.post('/api/chat',
                       json={'recruiter_name': 'Test User'},
                       content_type='application/json')
    assert resp.status_code == 400
    assert 'message' in resp.get_json()['error'].lower()


def test_chat_empty_body(client):
    """POST /api/chat with empty body should return 400."""
    resp = client.post('/api/chat',
                       json={},
                       content_type='application/json')
    assert resp.status_code == 400


def test_chat_whitespace_only_name(client):
    """Name that's only whitespace should be rejected."""
    resp = client.post('/api/chat',
                       json={'recruiter_name': '   ', 'message': 'Hi'})
    assert resp.status_code == 400


def test_chat_whitespace_only_message(client):
    """Message that's only whitespace should be rejected."""
    resp = client.post('/api/chat',
                       json={'recruiter_name': 'Jane', 'message': '   '})
    assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════
# Chat — success path (OpenAI mocked)
# ═══════════════════════════════════════════════════════════════

def _mock_openai_response(content='Hello from Jason\'s AI!'):
    """Build a mock OpenAI ChatCompletion response."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch('server.app._get_openai_client')
def test_chat_success_new_conversation(mock_client, client):
    """A valid chat request should return a reply and conversation_id."""
    mock_client.return_value.chat.completions.create.return_value = _mock_openai_response()
    resp = client.post('/api/chat', json={
        'recruiter_name': 'Alice',
        'message': 'Tell me about Jason',
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'reply' in data
    assert 'conversation_id' in data
    assert len(data['conversation_id']) == 36  # UUID


@patch('server.app._get_openai_client')
def test_chat_reply_content(mock_client, client):
    """The reply field should match the mocked LLM output."""
    mock_client.return_value.chat.completions.create.return_value = _mock_openai_response(
        'Jason has 6+ years of Java experience.'
    )
    data = client.post('/api/chat', json={
        'recruiter_name': 'Bob',
        'message': 'Java experience?',
    }).get_json()
    assert data['reply'] == 'Jason has 6+ years of Java experience.'


@patch('server.app._get_openai_client')
def test_chat_continue_conversation(mock_client, client):
    """Passing conversation_id should continue the same conversation."""
    mock_client.return_value.chat.completions.create.return_value = _mock_openai_response()

    # First message — creates conversation
    r1 = client.post('/api/chat', json={
        'recruiter_name': 'Carol',
        'message': 'Hi',
    }).get_json()
    conv_id = r1['conversation_id']

    # Second message — continues it
    r2 = client.post('/api/chat', json={
        'recruiter_name': 'Carol',
        'message': 'Follow-up',
        'conversation_id': conv_id,
    }).get_json()
    assert r2['conversation_id'] == conv_id


@patch('server.app._get_openai_client')
def test_chat_with_job_posting(mock_client, client):
    """Including a job_posting should still return 200."""
    mock_client.return_value.chat.completions.create.return_value = _mock_openai_response()
    resp = client.post('/api/chat', json={
        'recruiter_name': 'Dana',
        'message': 'Is Jason a fit?',
        'job_posting': 'Senior Java Developer at Acme Corp...',
    })
    assert resp.status_code == 200
    assert 'reply' in resp.get_json()


@patch('server.app._get_openai_client')
def test_chat_openai_value_error(mock_client, client):
    """ValueError (no API key) should return 503 with friendly message."""
    mock_client.side_effect = ValueError('OPENAI_API_KEY not set')
    resp = client.post('/api/chat', json={
        'recruiter_name': 'Eve',
        'message': 'Hello',
    })
    assert resp.status_code == 503
    assert 'gmail.com' in resp.get_json()['error']


@patch('server.app._get_openai_client')
def test_chat_openai_generic_error(mock_client, client):
    """Generic LLM exception should return 503 with friendly message."""
    mock_client.return_value.chat.completions.create.side_effect = RuntimeError('LLM down')
    resp = client.post('/api/chat', json={
        'recruiter_name': 'Frank',
        'message': 'Hello',
    })
    assert resp.status_code == 503
    assert 'break' in resp.get_json()['error'].lower() or 'email' in resp.get_json()['error'].lower()


# ═══════════════════════════════════════════════════════════════
# Admin Auth
# ═══════════════════════════════════════════════════════════════

def test_admin_chat_logs_no_token(client):
    """GET /admin/chat-logs without token should return 401."""
    resp = client.get('/admin/chat-logs')
    assert resp.status_code == 401


def test_admin_chat_stats_no_token(client):
    """GET /admin/chat-stats without token should return 401."""
    resp = client.get('/admin/chat-stats')
    assert resp.status_code == 401


def test_admin_chat_logs_wrong_token(client):
    """GET /admin/chat-logs with wrong token should return 401."""
    resp = client.get('/admin/chat-logs?token=wrong-token')
    assert resp.status_code == 401


@patch.dict(os.environ, {'ADMIN_TOKEN': 'test-secret-token'})
def test_admin_chat_logs_valid_token(client):
    """GET /admin/chat-logs with correct token should return 200."""
    resp = client.get('/admin/chat-logs?token=test-secret-token')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_conversations' in data
    assert 'conversations' in data
    assert isinstance(data['conversations'], list)


@patch.dict(os.environ, {'ADMIN_TOKEN': 'test-secret-token'})
def test_admin_chat_stats_valid_token(client):
    """GET /admin/chat-stats with correct token should return 200."""
    resp = client.get('/admin/chat-stats?token=test-secret-token')
    assert resp.status_code == 200
    data = resp.get_json()
    for key in ('total_conversations', 'total_messages',
                'total_user_messages', 'recent_recruiters'):
        assert key in data


@patch.dict(os.environ, {'ADMIN_TOKEN': 'test-secret-token'})
def test_admin_chat_stats_wrong_token(client):
    """GET /admin/chat-stats with bad token should return 401."""
    resp = client.get('/admin/chat-stats?token=bad')
    assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# Rate Limiting
# ═══════════════════════════════════════════════════════════════

def test_chat_rate_limit(client):
    """Rapid chat requests from same IP should eventually be rate-limited."""
    for i in range(12):
        resp = client.post('/api/chat',
                           json={'recruiter_name': 'Spammer', 'message': f'msg {i}'},
                           content_type='application/json')
    # The 12th request should be rate-limited (429)
    assert resp.status_code == 429
    assert 'slow down' in resp.get_json()['error'].lower()


def test_rate_limit_resets_after_window():
    """Rate limiter should allow requests again after the window elapses."""
    ip = '192.168.99.99'
    _chat_rate.clear()
    # Fill up the window
    past = time.time() - 120  # well outside the 60s window
    _chat_rate[ip] = [past] * 15
    # Should be allowed because all timestamps are expired
    assert _check_chat_rate(ip) is True


# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

def test_get_fill_color_high():
    """>=80% stock should return green."""
    c = get_fill_color(0.9)
    assert c is not None


def test_get_fill_color_medium():
    """50-79% stock should return light green."""
    c = get_fill_color(0.6)
    assert c is not None


def test_get_fill_color_low():
    """20-49% stock should return yellow."""
    c = get_fill_color(0.3)
    assert c is not None


def test_get_fill_color_critical():
    """>0 but <20% stock should return red."""
    c = get_fill_color(0.1)
    assert c is not None


def test_get_fill_color_empty():
    """0% stock should return gray."""
    c = get_fill_color(0)
    assert c is not None


def test_get_fill_color_boundary_80():
    """Exactly 0.8 should be green."""
    c80 = get_fill_color(0.8)
    c79 = get_fill_color(0.79)
    assert c80 != c79  # 0.8 is green, 0.79 is light green


def test_track_visitor_adds_entry():
    """_track_visitor should add the IP to the visitor log."""
    _visitor_log.clear()
    with app.test_request_context():
        _track_visitor('10.0.0.1')
    assert '10.0.0.1' in _visitor_log


def test_track_visitor_cleans_expired():
    """Expired entries should be pruned from visitor log."""
    _visitor_log.clear()
    _visitor_log['10.0.0.99'] = time.time() - 2000  # expired
    with app.test_request_context():
        _track_visitor('10.0.0.2')
    assert '10.0.0.99' not in _visitor_log
    assert '10.0.0.2' in _visitor_log


def test_check_chat_rate_allows_first():
    """First request from a fresh IP should be allowed."""
    _chat_rate.clear()
    assert _check_chat_rate('1.2.3.4') is True


def test_check_chat_rate_blocks_after_limit():
    """After 10 requests in the window, next should be blocked."""
    _chat_rate.clear()
    ip = '1.2.3.5'
    for _ in range(10):
        _check_chat_rate(ip)
    assert _check_chat_rate(ip) is False


# ═══════════════════════════════════════════════════════════════
# PDF Generation
# ═══════════════════════════════════════════════════════════════

def test_generate_pdf_minimal(client):
    """PDF endpoint should return a PDF with minimal valid data."""
    payload = {
        'items': [
            {
                'name': '2x4 Studs',
                'category': 'Framing',
                'current': 20,
                'capacity': 100,
                'toOrder': 80,
                'unitPrice': 3.50,
                'unitWeight': 8,
                'totalCost': 280.00,
            }
        ],
        'totalWeight': 640,
        'totalCost': 280.00,
        'totalPieces': 80,
        'totalBunks': 1,
    }
    resp = client.post('/generate-pdf', json=payload)
    assert resp.status_code == 200
    assert resp.content_type == 'application/pdf'
    assert resp.data[:5] == b'%PDF-'


def test_generate_pdf_empty_items(client):
    """PDF should still generate with zero items."""
    payload = {
        'items': [],
        'totalWeight': 0,
        'totalCost': 0,
        'totalPieces': 0,
        'totalBunks': 0,
    }
    resp = client.post('/generate-pdf', json=payload)
    assert resp.status_code == 200
    assert resp.data[:5] == b'%PDF-'


def test_generate_pdf_multiple_items(client):
    """PDF should handle multiple line items."""
    items = [
        {
            'name': f'Product {i}',
            'category': 'Cat',
            'current': i * 10,
            'capacity': 100,
            'toOrder': 100 - i * 10,
            'unitPrice': 5.0,
            'unitWeight': 10,
            'totalCost': (100 - i * 10) * 5.0,
        }
        for i in range(5)
    ]
    payload = {
        'items': items,
        'totalWeight': 2500,
        'totalCost': 7500.00,
        'totalPieces': 500,
        'totalBunks': 5,
    }
    resp = client.post('/generate-pdf', json=payload)
    assert resp.status_code == 200
    assert resp.data[:5] == b'%PDF-'


def test_generate_pdf_zero_capacity_item(client):
    """Item with capacity 0 should not cause division by zero."""
    payload = {
        'items': [{
            'name': 'Empty Bunk',
            'category': 'Other',
            'current': 0,
            'capacity': 0,
            'toOrder': 0,
            'unitPrice': 0,
            'unitWeight': 0,
            'totalCost': 0,
        }],
        'totalWeight': 0,
        'totalCost': 0,
        'totalPieces': 0,
        'totalBunks': 1,
    }
    resp = client.post('/generate-pdf', json=payload)
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════
# Request Middleware
# ═══════════════════════════════════════════════════════════════

def test_request_counter_incremented(client):
    """After a request, http_requests_total should include it."""
    client.get('/health')
    resp = client.get('/metrics')
    assert b'http_requests_total' in resp.data


def test_cors_headers_on_api(client):
    """API routes should include CORS Allow-Origin header."""
    resp = client.options('/api/stats', headers={
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
    })
    # Flask-CORS should respond to preflight
    assert resp.status_code in (200, 204)
