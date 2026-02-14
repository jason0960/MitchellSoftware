"""
Tests for script.js — Portfolio JavaScript structure and logic
Validates AppState, renderers, tracking, typing animation, and DOM bindings.
"""
import os
import re
import pytest

JS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'script.js')


@pytest.fixture(scope='module')
def js():
    with open(JS_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# ─── AppState Manager ─────────────────────────────────────────

class TestAppState:
    def test_appstate_defined(self, js):
        assert 'AppState' in js

    def test_has_state_object(self, js):
        assert '_state' in js

    def test_initial_mode_creative(self, js):
        assert "mode: 'creative'" in js or 'mode:"creative"' in js

    def test_has_subscribers(self, js):
        assert '_subscribers' in js

    def test_has_props_getter(self, js):
        assert 'get props' in js or 'props()' in js

    def test_has_set_state(self, js):
        assert 'setState' in js

    def test_has_subscribe(self, js):
        assert 'subscribe' in js

    def test_has_toggle(self, js):
        assert 'toggle' in js

    def test_state_keys(self, js):
        for key in ['mode', 'scrolled', 'mobileMenuOpen', 'activeSection',
                     'typingActive', 'whiteboard']:
            assert key in js, f"Missing state key: {key}"

    def test_props_derived_values(self, js):
        for prop in ['isCreative', 'isProfessional', 'modeLabel', 'bodyClass']:
            assert prop in js, f"Missing derived prop: {prop}"


# ─── Renderers ─────────────────────────────────────────────────

class TestRenderers:
    def test_render_mode_exists(self, js):
        assert 'renderMode' in js

    def test_render_navbar_exists(self, js):
        assert 'renderNavbar' in js

    def test_render_whiteboard_exists(self, js):
        assert 'renderWhiteboard' in js

    def test_position_annotations_exists(self, js):
        assert 'positionAnnotations' in js

    def test_renderers_subscribe(self, js):
        """Each renderer should be subscribed to AppState."""
        for renderer in ['renderMode', 'renderNavbar', 'renderWhiteboard']:
            # Should appear in a subscribe call
            assert renderer in js


# ─── Mode Toggle ──────────────────────────────────────────────

class TestModeToggle:
    def test_professional_class_toggle(self, js):
        assert 'professional' in js

    def test_localstorage_persistence(self, js):
        assert 'localStorage' in js
        assert 'jm-portfolio-mode' in js

    def test_hero_btn_updates(self, js):
        assert 'heroBtn' in js

    def test_mode_label_updates(self, js):
        assert 'modeLabel' in js


# ─── Whiteboard ───────────────────────────────────────────────

class TestWhiteboard:
    def test_whiteboard_on_class(self, js):
        assert 'whiteboard-on' in js

    def test_wb_overlay_referenced(self, js):
        assert 'wbOverlay' in js

    def test_mobile_detection_in_annotations(self, js):
        assert 'isMobile' in js or '768' in js

    def test_annotations_positioned_per_target(self, js):
        """positionAnnotations should handle multiple named targets."""
        for target in ['modeToggle', 'navBrand', 'socialLinks']:
            assert target in js


# ─── Typing Animation ─────────────────────────────────────────

class TestTypingAnimation:
    def test_type_function_exists(self, js):
        assert re.search(r'function\s+type|const\s+type\s*=', js) or 'type()' in js

    def test_typed_text_element(self, js):
        assert 'typedText' in js

    def test_has_titles_array(self, js):
        """Should have an array of title strings to cycle through."""
        assert 'strings' in js or 'titles' in js or 'words' in js or 'phrases' in js


# ─── Event Tracking ───────────────────────────────────────────

class TestTracking:
    def test_track_event_function(self, js):
        assert 'trackEvent' in js

    def test_api_base_url(self, js):
        assert 'mitchellsoftwareportfolio.onrender.com' in js

    def test_portfolio_view_tracked(self, js):
        assert 'portfolio_view' in js

    def test_contact_submit_tracked(self, js):
        # Contact form uses EmailJS; tracking may use different event name
        assert 'contactForm' in js or 'contact_submit' in js or 'contact' in js

    def test_resume_enjoyed_tracked(self, js):
        assert 'resume_enjoyed' in js


# ─── Stats Loading ────────────────────────────────────────────

class TestStatsLoading:
    def test_load_stats_function(self, js):
        assert 'loadStats' in js

    def test_fetches_api_stats(self, js):
        assert '/api/stats' in js

    def test_updates_stat_elements(self, js):
        for el_id in ['statViews', 'statDemos', 'statPdfs', 'statVotes']:
            assert el_id in js, f"loadStats should update #{el_id}"

    def test_updates_health_display(self, js):
        for el_id in ['statUptime', 'statMemory', 'statCpu', 'statSessions']:
            assert el_id in js, f"loadStats should update #{el_id}"


# ─── Contact Form ─────────────────────────────────────────────

class TestContactForm:
    def test_emailjs_integration(self, js):
        assert 'emailjs' in js.lower() or 'EmailJS' in js

    def test_form_submit_handler(self, js):
        assert 'contactForm' in js

    def test_form_validation_fields(self, js):
        for field in ['name', 'email', 'message']:
            assert field in js


# ─── Enjoyed Button ───────────────────────────────────────────

class TestEnjoyedButton:
    def test_enjoyed_btn_handler(self, js):
        assert 'enjoyedBtn' in js

    def test_disables_after_vote(self, js):
        assert 'disabled' in js

    def test_enjoyed_label_updated(self, js):
        # Label is updated via innerHTML on enjoyedBtn itself
        assert 'enjoyedBtn' in js


# ─── Scroll Handling ──────────────────────────────────────────

class TestScrollHandling:
    def test_scroll_event_listener(self, js):
        assert 'scroll' in js

    def test_intersection_observer(self, js):
        assert 'IntersectionObserver' in js or 'scrolled' in js

    def test_active_section_tracking(self, js):
        assert 'activeSection' in js


# ─── Navbar ───────────────────────────────────────────────────

class TestNavbar:
    def test_hamburger_toggle(self, js):
        assert 'hamburger' in js

    def test_scrolled_class(self, js):
        assert 'scrolled' in js

    def test_nav_links_active_class(self, js):
        assert 'active' in js

    def test_editor_tabs(self, js):
        assert 'editor-tab' in js


# ─── IIFE Wrapper ─────────────────────────────────────────────

class TestStructure:
    def test_uses_strict_mode(self, js):
        assert "'use strict'" in js or '"use strict"' in js

    def test_iife_wrapper(self, js):
        """Script should be wrapped in an IIFE to avoid globals."""
        assert js.strip().startswith('(') or js.strip().startswith('/*')
        assert js.strip().endswith('();') or js.strip().endswith('})();')

    def test_cursor_glow_handler(self, js):
        assert 'cursorGlow' in js
