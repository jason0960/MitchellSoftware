"""
Tests for styles.css — Portfolio CSS structure and responsive design
Validates critical selectors, CSS variables, responsive breakpoints,
whiteboard mobile behavior, and the Try Me button callout.
"""
import os
import re
import pytest

CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'styles.css')


@pytest.fixture(scope='module')
def css():
    with open(CSS_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# ─── CSS Variables ─────────────────────────────────────────────

class TestCSSVariables:
    REQUIRED_VARS = [
        '--bg-primary',
        '--bg-secondary',
        '--bg-card',
        '--text-primary',
        '--text-secondary',
        '--accent',
        '--border',
        '--font-mono',
    ]

    @pytest.mark.parametrize('var', REQUIRED_VARS)
    def test_variable_defined(self, css, var):
        assert var in css, f"CSS variable {var} not defined"

    def test_accent_is_hd_orange(self, css):
        """Accent color should be Home Depot orange #F96302."""
        pattern = r'--accent\s*:\s*#[Ff]96302'
        assert re.search(pattern, css), "Accent color is not #F96302"

    def test_font_mono_is_jetbrains(self, css):
        pattern = r"--font-mono\s*:.*JetBrains\s*Mono"
        assert re.search(pattern, css), "Mono font is not JetBrains Mono"


# ─── Core Layout Selectors ────────────────────────────────────

class TestCoreSelectors:
    REQUIRED_SELECTORS = [
        '.navbar',
        '.hero',
        '.hero-content',
        '.work-card',
        '.skill-category',
        '.timeline',
        '.section-title',
        '.contact-form',
    ]

    @pytest.mark.parametrize('selector', REQUIRED_SELECTORS)
    def test_selector_exists(self, css, selector):
        assert selector in css, f"Required selector '{selector}' missing from CSS"


# ─── Try Me Button Styles ─────────────────────────────────────

class TestTryMeButton:
    def test_btn_try_me_exists(self, css):
        assert '.btn-try-me' in css

    def test_has_border(self, css):
        # Find the .btn-try-me block
        idx = css.find('.btn-try-me')
        block = css[idx:idx + 500]
        assert 'border' in block

    def test_has_accent_color(self, css):
        idx = css.find('.btn-try-me')
        block = css[idx:idx + 500]
        assert 'var(--accent)' in block or '#F96302' in block or '#f96302' in block

    def test_has_hover_state(self, css):
        assert '.btn-try-me:hover' in css

    def test_has_transition(self, css):
        idx = css.find('.btn-try-me')
        block = css[idx:idx + 500]
        assert 'transition' in block

    def test_has_pulse_animation(self, css):
        assert 'tryMePulse' in css

    def test_hover_removes_animation(self, css):
        hover_idx = css.find('.btn-try-me:hover')
        hover_block = css[hover_idx:hover_idx + 300]
        assert 'animation: none' in hover_block or 'animation:none' in hover_block

    def test_has_font_mono(self, css):
        idx = css.find('.btn-try-me')
        block = css[idx:idx + 500]
        assert 'font-mono' in block or 'monospace' in block or 'JetBrains' in block


# ─── Whiteboard Mobile ────────────────────────────────────────

class TestWhiteboardMobile:
    def _get_mobile_block(self, css):
        """Extract the last @media (max-width: 768px) block containing wb-overlay."""
        # Find the wb-overlay mobile block by locating it in the CSS
        idx = css.rfind('.wb-overlay')
        if idx == -1:
            return ''
        # Walk backwards to find the @media opening
        media_start = css.rfind('@media', 0, idx)
        if media_start == -1:
            return ''
        # Walk forward from media_start to find matching closing brace
        depth = 0
        end = media_start
        for i in range(media_start, len(css)):
            if css[i] == '{':
                depth += 1
            elif css[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        return css[media_start:end]

    def test_wb_overlay_hidden_on_mobile(self, css):
        block = self._get_mobile_block(css)
        assert 'display: none' in block or 'display:none' in block, \
            "wb-overlay should be hidden on mobile"

    def test_wb_overlay_uses_important(self, css):
        block = self._get_mobile_block(css)
        assert '!important' in block, \
            "wb-overlay display:none should use !important"

    def test_whiteboard_btn_hidden_on_mobile(self, css):
        block = self._get_mobile_block(css)
        assert '#whiteboardBtn' in block, \
            "Whiteboard button should be hidden on mobile"


# ─── Responsive Design ────────────────────────────────────────

class TestResponsive:
    def test_has_media_queries(self, css):
        matches = re.findall(r'@media', css)
        assert len(matches) >= 2, "Should have multiple media queries"

    def test_has_mobile_breakpoint(self, css):
        assert '768px' in css

    def test_work_grid_responsive(self, css):
        assert 'work-grid' in css or 'workGrid' in css

    def test_nav_menu_mobile(self, css):
        assert 'navMenu' in css or 'nav-menu' in css


# ─── Professional Mode ────────────────────────────────────────

class TestProfessionalMode:
    def test_professional_class_exists(self, css):
        assert '.professional' in css or 'body.professional' in css

    def test_whiteboard_btn_hidden_in_professional(self, css):
        """In professional mode, whiteboard button uses default display:none."""
        assert '#whiteboardBtn' in css
        # The default state is display:none, creative mode shows it
        idx = css.find('#whiteboardBtn')
        block = css[idx:idx + 200]
        assert 'display: none' in block or 'display:none' in block


# ─── Work Card Styles ─────────────────────────────────────────

class TestWorkCard:
    def test_has_background(self, css):
        idx = css.find('.work-card')
        block = css[idx:idx + 500]
        assert 'background' in block

    def test_has_border_radius(self, css):
        idx = css.find('.work-card')
        block = css[idx:idx + 500]
        assert 'border-radius' in block

    def test_has_hover_effect(self, css):
        assert '.work-card:hover' in css

    def test_has_padding(self, css):
        idx = css.find('.work-card')
        block = css[idx:idx + 500]
        assert 'padding' in block


# ─── Animations ───────────────────────────────────────────────

class TestAnimations:
    def test_has_keyframes(self, css):
        matches = re.findall(r'@keyframes', css)
        assert len(matches) >= 1, "Should have at least one @keyframes animation"

    def test_has_transitions(self, css):
        matches = re.findall(r'transition\s*:', css)
        assert len(matches) >= 5, "Should have multiple transitions for smooth UX"


# ─── Whiteboard Annotations ──────────────────────────────────

class TestWhiteboardAnnotationStyles:
    def test_wb_annotation_exists(self, css):
        assert '.wb-annotation' in css

    def test_wb_label_exists(self, css):
        assert '.wb-label' in css

    def test_wb_arrow_exists(self, css):
        assert '.wb-arrow' in css

    def test_wb_overlay_exists(self, css):
        assert '.wb-overlay' in css
