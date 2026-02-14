"""
Tests for pallet-builder.html — Lumber Yard Restock Planner HTML structure
Validates DOM elements, required UI controls, and accessibility.
"""
import os
import re
import pytest

HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'pallet-builder.html')


@pytest.fixture(scope='module')
def html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# ─── Head & Meta ───────────────────────────────────────────────

class TestMeta:
    def test_has_viewport(self, html):
        assert 'viewport' in html

    def test_has_title(self, html):
        assert '<title>' in html
        assert 'Lumber Yard' in html or 'Restock' in html

    def test_loads_threejs(self, html):
        assert 'three' in html.lower()

    def test_loads_orbit_controls(self, html):
        assert 'OrbitControls' in html

    def test_loads_stylesheet(self, html):
        assert 'pallet-builder.css' in html

    def test_loads_script(self, html):
        assert 'pallet-builder.js' in html


# ─── 3D Canvas ────────────────────────────────────────────────

class TestCanvas:
    def test_has_yard_canvas(self, html):
        assert 'yardCanvas' in html

    def test_has_hover_hint(self, html):
        assert 'hoverHint' in html

    def test_has_item_tooltip(self, html):
        assert 'itemTooltip' in html


# ─── Controls ─────────────────────────────────────────────────

class TestControls:
    CONTROL_IDS = [
        'rotateLeftBtn',
        'resetViewBtn',
        'rotateRightBtn',
        'randomizeBtn',
        'searchInput',
        'themeToggle',
    ]

    @pytest.mark.parametrize('control_id', CONTROL_IDS)
    def test_control_exists(self, html, control_id):
        assert f'id="{control_id}"' in html

    def test_has_category_tabs(self, html):
        assert 'categoryTabs' in html


# ─── Sidebar ──────────────────────────────────────────────────

class TestSidebar:
    def test_sidebar_exists(self, html):
        assert 'pbSidebar' in html

    def test_sidebar_toggle(self, html):
        assert 'sidebarToggle' in html

    def test_close_sidebar(self, html):
        assert 'closeSidebar' in html

    def test_sidebar_backdrop(self, html):
        assert 'sidebarBackdrop' in html

    def test_has_cart_list(self, html):
        assert 'cartList' in html

    def test_has_cart_badge(self, html):
        assert 'cartBadge' in html

    def test_has_weight_bar(self, html):
        assert 'weightBar' in html

    def test_has_weight_label(self, html):
        assert 'weightLabel' in html

    def test_has_weight_max(self, html):
        assert 'weightMax' in html


# ─── Summary Counters ─────────────────────────────────────────

class TestSummary:
    SUMMARY_IDS = ['totalItems', 'totalQty', 'totalPrice']

    @pytest.mark.parametrize('element_id', SUMMARY_IDS)
    def test_summary_element_exists(self, html, element_id):
        assert f'id="{element_id}"' in html

    def test_has_generate_pdf_btn(self, html):
        assert 'generatePdfBtn' in html

    def test_has_clear_cart_btn(self, html):
        assert 'clearCartBtn' in html

    def test_has_status_msg(self, html):
        assert 'statusMsg' in html


# ─── Yard Health ──────────────────────────────────────────────

class TestYardHealth:
    HEALTH_IDS = ['fullCount', 'lowCount', 'critCount']

    @pytest.mark.parametrize('health_id', HEALTH_IDS)
    def test_health_indicator_exists(self, html, health_id):
        assert f'id="{health_id}"' in html


# ─── Accessibility ────────────────────────────────────────────

class TestAccessibility:
    def test_html_lang_attribute(self, html):
        assert 'lang=' in html

    def test_search_has_placeholder(self, html):
        pattern = r'id="searchInput"[^>]*placeholder='
        assert re.search(pattern, html), "Search input missing placeholder"
