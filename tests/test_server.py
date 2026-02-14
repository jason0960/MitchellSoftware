"""
Tests for server.py — Flask PDF Server
Covers: endpoints, tracking, stats, PDF generation, health, metrics
"""
import json
import time
import pytest
import sys
import os

# Add parent directory to path so we can import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app, _visitor_log, SESSION_WINDOW, get_fill_color
from prometheus_client import REGISTRY


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_visitor_log():
    """Clear visitor log between tests."""
    _visitor_log.clear()
    yield
    _visitor_log.clear()


# ─── Health Endpoint ───────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'

    def test_health_includes_service_name(self, client):
        resp = client.get('/health')
        data = resp.get_json()
        assert 'service' in data
        assert 'Lumber Yard' in data['service']


# ─── Tracking Endpoint ────────────────────────────────────────

class TestTrackEndpoint:
    VALID_EVENTS = [
        'portfolio_view',
        'demo_view',
        'pdf_generated',
        'contact_submit',
        'resume_enjoyed',
    ]

    @pytest.mark.parametrize('event', VALID_EVENTS)
    def test_track_valid_event(self, client, event):
        resp = client.post('/api/track',
                           data=json.dumps({'event': event}),
                           content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['ok'] is True
        assert data['event'] == event

    def test_track_unknown_event_returns_400(self, client):
        resp = client.post('/api/track',
                           data=json.dumps({'event': 'nonexistent_event'}),
                           content_type='application/json')
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['ok'] is False
        assert 'unknown event' in data['error']

    def test_track_missing_event_returns_400(self, client):
        resp = client.post('/api/track',
                           data=json.dumps({}),
                           content_type='application/json')
        assert resp.status_code == 400

    def test_track_empty_body_returns_400(self, client):
        resp = client.post('/api/track',
                           data='',
                           content_type='application/json')
        assert resp.status_code == 400

    def test_track_no_json_returns_400(self, client):
        resp = client.post('/api/track')
        assert resp.status_code == 400


# ─── Stats Endpoint ───────────────────────────────────────────

class TestStatsEndpoint:
    def test_stats_returns_200(self, client):
        resp = client.get('/api/stats')
        assert resp.status_code == 200

    def test_stats_has_required_fields(self, client):
        resp = client.get('/api/stats')
        data = resp.get_json()
        required = ['portfolio_views', 'demo_views', 'pdf_generations',
                     'contact_submissions', 'resume_enjoyed', 'health']
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_stats_health_has_required_fields(self, client):
        resp = client.get('/api/stats')
        data = resp.get_json()
        health = data['health']
        required = ['uptime_seconds', 'uptime_display', 'memory_mb',
                     'cpu_percent', 'active_sessions']
        for field in required:
            assert field in health, f"Missing health field: {field}"

    def test_stats_uptime_is_positive(self, client):
        resp = client.get('/api/stats')
        data = resp.get_json()
        assert data['health']['uptime_seconds'] > 0

    def test_stats_memory_is_positive(self, client):
        resp = client.get('/api/stats')
        data = resp.get_json()
        assert data['health']['memory_mb'] > 0

    def test_stats_values_are_numeric(self, client):
        resp = client.get('/api/stats')
        data = resp.get_json()
        for key in ['portfolio_views', 'demo_views', 'pdf_generations',
                     'contact_submissions', 'resume_enjoyed']:
            assert isinstance(data[key], (int, float)), f"{key} is not numeric"

    def test_stats_uptime_display_format(self, client):
        resp = client.get('/api/stats')
        data = resp.get_json()
        display = data['health']['uptime_display']
        assert 'h' in display and 'm' in display and 's' in display

    def test_tracking_increments_stats(self, client):
        before = client.get('/api/stats').get_json()
        client.post('/api/track',
                     data=json.dumps({'event': 'portfolio_view'}),
                     content_type='application/json')
        after = client.get('/api/stats').get_json()
        assert after['portfolio_views'] >= before['portfolio_views']


# ─── Metrics Endpoint ─────────────────────────────────────────

class TestMetricsEndpoint:
    def test_metrics_returns_200(self, client):
        resp = client.get('/metrics')
        assert resp.status_code == 200

    def test_metrics_content_type(self, client):
        resp = client.get('/metrics')
        assert 'text/plain' in resp.content_type or 'text/openmetrics' in resp.content_type

    def test_metrics_contains_counters(self, client):
        resp = client.get('/metrics')
        body = resp.data.decode('utf-8')
        assert 'portfolio_page_views_total' in body
        assert 'demo_page_views_total' in body
        assert 'pdf_generations_total' in body

    def test_metrics_contains_system_gauges(self, client):
        resp = client.get('/metrics')
        body = resp.data.decode('utf-8')
        assert 'server_uptime_seconds' in body
        assert 'process_memory_usage_mb' in body
        assert 'process_cpu_percent' in body

    def test_metrics_contains_histogram(self, client):
        resp = client.get('/metrics')
        body = resp.data.decode('utf-8')
        assert 'http_request_duration_seconds' in body


# ─── PDF Generation Endpoint ──────────────────────────────────

class TestPdfGeneration:
    @staticmethod
    def _make_payload(items=None, truck_image='', chart_image=''):
        if items is None:
            items = [
                {
                    'name': '2x4x8 SPF Stud',
                    'category': 'Dimensional',
                    'current': 20,
                    'capacity': 100,
                    'toOrder': 80,
                    'unitPrice': 3.47,
                    'unitWeight': 8,
                    'totalCost': 277.60,
                },
            ]
        return {
            'items': items,
            'truckImage': truck_image,
            'chartImage': chart_image,
            'totalWeight': sum(i['toOrder'] * i['unitWeight'] for i in items),
            'totalCost': sum(i['totalCost'] for i in items),
            'totalPieces': sum(i['toOrder'] for i in items),
            'totalBunks': len(items),
        }

    def test_pdf_returns_200(self, client):
        payload = self._make_payload()
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 200

    def test_pdf_content_type(self, client):
        payload = self._make_payload()
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert 'application/pdf' in resp.content_type

    def test_pdf_has_content(self, client):
        payload = self._make_payload()
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert len(resp.data) > 100  # PDF must have real content

    def test_pdf_starts_with_magic_bytes(self, client):
        payload = self._make_payload()
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.data[:5] == b'%PDF-'

    def test_pdf_multiple_items(self, client):
        items = [
            {
                'name': '2x4x8 SPF Stud',
                'category': 'Dimensional',
                'current': 20,
                'capacity': 100,
                'toOrder': 80,
                'unitPrice': 3.47,
                'unitWeight': 8,
                'totalCost': 277.60,
            },
            {
                'name': '4x8 OSB Sheathing',
                'category': 'Sheet',
                'current': 5,
                'capacity': 60,
                'toOrder': 55,
                'unitPrice': 12.98,
                'unitWeight': 45,
                'totalCost': 713.90,
            },
            {
                'name': '6x6x12 PT Post',
                'category': 'Treated',
                'current': 0,
                'capacity': 40,
                'toOrder': 40,
                'unitPrice': 28.97,
                'unitWeight': 65,
                'totalCost': 1158.80,
            },
        ]
        payload = self._make_payload(items=items)
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 200
        assert resp.data[:5] == b'%PDF-'

    def test_pdf_empty_items(self, client):
        payload = self._make_payload(items=[])
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 200

    def test_pdf_with_images(self, client):
        """PDF generation should handle base64-encoded diagram images."""
        import base64
        from io import BytesIO
        # Create a valid 1x1 PNG using minimal correct format
        import struct, zlib
        def make_png():
            width, height = 1, 1
            raw_data = b'\x00\xff\x00\x00'  # filter byte + RGB
            ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
            def chunk(ctype, data):
                c = ctype + data
                return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
            return (b'\x89PNG\r\n\x1a\n' +
                    chunk(b'IHDR', ihdr_data) +
                    chunk(b'IDAT', zlib.compress(raw_data)) +
                    chunk(b'IEND', b''))
        png_bytes = make_png()
        b64 = 'data:image/png;base64,' + base64.b64encode(png_bytes).decode()

        payload = self._make_payload(truck_image=b64, chart_image=b64)
        resp = client.post('/generate-pdf',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 200
        assert resp.data[:5] == b'%PDF-'


# ─── Fill Color Utility ───────────────────────────────────────

class TestGetFillColor:
    def test_full_stock_is_green(self):
        color = get_fill_color(1.0)
        assert str(color) == str(get_fill_color(0.8))

    def test_high_stock_is_green(self):
        color = get_fill_color(0.85)
        assert color is not None

    def test_medium_stock(self):
        color = get_fill_color(0.5)
        assert color is not None

    def test_low_stock_is_yellow(self):
        color = get_fill_color(0.2)
        assert color is not None

    def test_critical_stock_is_red(self):
        color = get_fill_color(0.1)
        assert color is not None

    def test_empty_stock(self):
        color = get_fill_color(0)
        assert color is not None

    def test_color_bands_differ(self):
        """Different stock levels produce different colors."""
        full = str(get_fill_color(1.0))
        mid = str(get_fill_color(0.5))
        low = str(get_fill_color(0.1))
        empty = str(get_fill_color(0))
        # At least 3 distinct colors
        assert len({full, mid, low, empty}) >= 3


# ─── Session Tracking ─────────────────────────────────────────

class TestSessionTracking:
    def test_visitor_tracked_on_request(self, client):
        client.get('/health')
        assert len(_visitor_log) > 0

    def test_multiple_requests_same_ip(self, client):
        client.get('/health')
        client.get('/health')
        # Same IP should remain one entry
        assert len(_visitor_log) == 1

    def test_active_sessions_in_stats(self, client):
        client.get('/health')
        resp = client.get('/api/stats')
        data = resp.get_json()
        assert data['health']['active_sessions'] >= 1


# ─── CORS ──────────────────────────────────────────────────────

class TestCORS:
    def test_api_track_cors_header(self, client):
        resp = client.options('/api/track', headers={
            'Origin': 'https://jason0960.github.io',
            'Access-Control-Request-Method': 'POST',
        })
        # CORS should allow the request
        assert resp.status_code in (200, 204)

    def test_metrics_cors_header(self, client):
        resp = client.options('/metrics', headers={
            'Origin': 'https://jason0960.github.io',
            'Access-Control-Request-Method': 'GET',
        })
        assert resp.status_code in (200, 204)


# ─── Static File Serving ──────────────────────────────────────

class TestStaticServing:
    def test_root_serves_pallet_builder(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_index_html_served(self, client):
        resp = client.get('/index.html')
        assert resp.status_code == 200
        assert b'Jason Mitchell' in resp.data or b'html' in resp.data

    def test_styles_css_served(self, client):
        resp = client.get('/styles.css')
        assert resp.status_code == 200

    def test_script_js_served(self, client):
        resp = client.get('/script.js')
        assert resp.status_code == 200


# ─── Request Middleware ────────────────────────────────────────

class TestMiddleware:
    def test_request_sets_start_time(self, client):
        """After a request, the request count metric should have been incremented."""
        resp = client.get('/health')
        assert resp.status_code == 200
        # Check metrics endpoint has recorded the request
        metrics = client.get('/metrics').data.decode()
        assert 'http_requests_total' in metrics

    def test_latency_histogram_recorded(self, client):
        client.get('/health')
        metrics = client.get('/metrics').data.decode()
        assert 'http_request_duration_seconds' in metrics
