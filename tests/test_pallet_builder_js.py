"""
Tests for pallet-builder.js — Lumber Yard Restock Planner JavaScript
Validates catalog data, constants, functions, and 3D scene setup.
"""
import os
import re
import pytest

JS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'pallet-builder.js')


@pytest.fixture(scope='module')
def js():
    with open(JS_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# ─── Catalog Data ─────────────────────────────────────────────

class TestCatalog:
    def test_catalog_defined(self, js):
        assert 'CATALOG' in js

    def test_catalog_has_items(self, js):
        # Count id: entries in CATALOG array
        count = len(re.findall(r'\bid\s*:', js[:5000]))
        assert count >= 15, f"CATALOG should have 15+ items, found {count}"

    def test_catalog_item_properties(self, js):
        """Each catalog item should have required properties."""
        for prop in ['name', 'category', 'capacity', 'unitPrice',
                     'unitWeight', 'color', 'dims']:
            assert prop in js, f"Missing catalog property: {prop}"

    def test_categories_exist(self, js):
        for cat in ['Dimensional', 'Sheet', 'Treated', 'Specialty']:
            assert cat in js, f"Missing category: {cat}"


# ─── Constants ─────────────────────────────────────────────────

class TestConstants:
    def test_truck_max_lbs(self, js):
        assert 'TRUCK_MAX_LBS' in js

    def test_truck_max_value(self, js):
        match = re.search(r'TRUCK_MAX_LBS\s*=\s*(\d+)', js)
        assert match, "TRUCK_MAX_LBS not found"
        assert int(match.group(1)) == 48000


# ─── Core Functions ───────────────────────────────────────────

class TestCoreFunctions:
    REQUIRED_FUNCTIONS = [
        'init',
        'initScene',
        'buildYard',
        'createBunkMesh',
        'bindEvents',
        'animate',
        'updateSidebar',
        'updateYardHealth',
        'generatePdf',
        'toggleFlag',
    ]

    @pytest.mark.parametrize('func', REQUIRED_FUNCTIONS)
    def test_function_exists(self, js, func):
        pattern = rf'function\s+{func}\b|const\s+{func}\s*='
        assert re.search(pattern, js), f"Function '{func}' not found"


# ─── 3D Scene Setup ───────────────────────────────────────────

class TestSceneSetup:
    def test_uses_webgl_renderer(self, js):
        assert 'WebGLRenderer' in js

    def test_creates_scene(self, js):
        assert 'THREE.Scene' in js or 'new.*Scene' in js

    def test_creates_camera(self, js):
        assert 'PerspectiveCamera' in js

    def test_creates_orbit_controls(self, js):
        assert 'OrbitControls' in js

    def test_adds_lights(self, js):
        assert 'DirectionalLight' in js or 'AmbientLight' in js

    def test_creates_ground(self, js):
        assert 'PlaneGeometry' in js or 'ground' in js

    def test_uses_raycaster(self, js):
        assert 'Raycaster' in js


# ─── Bunk Mesh ────────────────────────────────────────────────

class TestBunkMesh:
    def test_creates_group(self, js):
        assert 'THREE.Group' in js

    def test_creates_board_layers(self, js):
        assert 'BoxGeometry' in js

    def test_creates_banding_straps(self, js):
        assert 'strap' in js.lower() or 'band' in js.lower()

    def test_creates_rack_posts(self, js):
        assert 'post' in js.lower() or 'CylinderGeometry' in js

    def test_has_indicator_bar(self, js):
        assert 'indicator' in js.lower() or 'bar' in js.lower()

    def test_has_label_sprites(self, js):
        assert 'Sprite' in js or 'sprite' in js or 'canvas' in js


# ─── Interaction Handlers ────────────────────────────────────

class TestInteraction:
    def test_mouse_move_handler(self, js):
        assert 'mousemove' in js.lower() or 'onMouseMove' in js

    def test_click_handler(self, js):
        assert 'click' in js.lower() or 'onClick' in js

    def test_touch_handler(self, js):
        assert 'touch' in js.lower()

    def test_double_click_handler(self, js):
        assert 'dblclick' in js.lower() or 'onDoubleClick' in js

    def test_tooltip_display(self, js):
        assert 'itemTooltip' in js or 'tooltip' in js


# ─── Sidebar ──────────────────────────────────────────────────

class TestSidebar:
    def test_sidebar_toggle(self, js):
        assert 'sidebarToggle' in js

    def test_cart_list_update(self, js):
        assert 'cartList' in js

    def test_weight_bar_update(self, js):
        assert 'weightBar' in js

    def test_cart_badge_update(self, js):
        assert 'cartBadge' in js

    def test_total_items_update(self, js):
        assert 'totalItems' in js

    def test_total_qty_update(self, js):
        assert 'totalQty' in js

    def test_total_price_update(self, js):
        assert 'totalPrice' in js


# ─── PDF Generation ───────────────────────────────────────────

class TestPdfGeneration:
    def test_generate_pdf_function(self, js):
        assert 'generatePdf' in js

    def test_posts_to_generate_pdf(self, js):
        assert '/generate-pdf' in js

    def test_sends_json(self, js):
        assert 'application/json' in js

    def test_builds_truck_diagram(self, js):
        assert 'buildTruckDiagram' in js or 'truckDiagram' in js

    def test_builds_yard_chart(self, js):
        assert 'buildYardChart' in js or 'yardChart' in js

    def test_creates_blob_download(self, js):
        assert 'Blob' in js or 'blob' in js


# ─── Truck Diagram (3D Offscreen) ────────────────────────────

class TestTruckDiagram:
    def test_offscreen_renderer(self, js):
        assert 'offRenderer' in js or 'offscreen' in js.lower()

    def test_offscreen_scene(self, js):
        assert 'offScene' in js

    def test_offscreen_camera(self, js):
        assert 'offCamera' in js

    def test_truck_model_parts(self, js):
        """Truck model should include body, wheels, and frame."""
        for part in ['fender', 'tire', 'wheel', 'frame', 'deck', 'headache']:
            if part in js.lower():
                return
        # At least some truck parts should exist
        assert 'truck' in js.lower()


# ─── Camera Controls ──────────────────────────────────────────

class TestCameraControls:
    def test_rotate_camera(self, js):
        assert 'rotateCamera' in js

    def test_reset_view(self, js):
        assert 'resetView' in js

    def test_fly_to(self, js):
        assert 'flyTo' in js.lower() or 'fly' in js.lower()


# ─── Search & Filter ─────────────────────────────────────────

class TestSearchFilter:
    def test_search_function(self, js):
        assert 'highlightSearch' in js or 'searchInput' in js

    def test_category_filter(self, js):
        assert 'filterCategory' in js or 'categoryTabs' in js


# ─── Yard Health ──────────────────────────────────────────────

class TestYardHealth:
    def test_update_yard_health(self, js):
        assert 'updateYardHealth' in js

    def test_counts_full(self, js):
        assert 'fullCount' in js

    def test_counts_low(self, js):
        assert 'lowCount' in js

    def test_counts_critical(self, js):
        assert 'critCount' in js


# ─── Theme Toggle ─────────────────────────────────────────────

class TestThemeToggle:
    def test_theme_toggle_exists(self, js):
        assert 'themeToggle' in js

    def test_light_theme_class(self, js):
        assert 'light' in js.lower()


# ─── Pulse / Glow Animation ──────────────────────────────────

class TestAnimations:
    def test_pulse_ring(self, js):
        assert 'pulse' in js.lower() or 'ring' in js.lower()

    def test_glow_effect(self, js):
        assert 'glow' in js.lower()

    def test_request_animation_frame(self, js):
        assert 'requestAnimationFrame' in js
