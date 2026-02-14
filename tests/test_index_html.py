"""
Tests for index.html — Portfolio HTML structure, accessibility, and content
Validates DOM structure, required elements, links, and meta tags.
"""
import os
import re
import pytest

HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')


@pytest.fixture(scope='module')
def html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# ─── Meta & Head ───────────────────────────────────────────────

class TestMeta:
    def test_has_viewport_meta(self, html):
        assert 'viewport' in html

    def test_has_charset(self, html):
        assert 'charset' in html.lower() or 'UTF-8' in html

    def test_has_title(self, html):
        assert '<title>' in html

    def test_viewport_fit_cover(self, html):
        assert 'viewport-fit=cover' in html

    def test_loads_font_awesome(self, html):
        assert 'font-awesome' in html.lower() or 'fontawesome' in html.lower()

    def test_loads_google_fonts(self, html):
        assert 'fonts.googleapis.com' in html

    def test_loads_jetbrains_mono(self, html):
        assert 'JetBrains+Mono' in html or 'JetBrains Mono' in html

    def test_loads_stylesheet(self, html):
        assert 'styles.css' in html

    def test_loads_script(self, html):
        assert 'script.js' in html


# ─── Navigation ────────────────────────────────────────────────

class TestNavigation:
    def test_has_navbar(self, html):
        assert 'navbar' in html

    def test_has_nav_brand(self, html):
        assert 'navBrand' in html or 'nav-brand' in html

    def test_has_hamburger(self, html):
        assert 'hamburger' in html

    def test_has_mode_toggle(self, html):
        assert 'modeToggle' in html

    def test_has_editor_tabs(self, html):
        assert 'editor-tab' in html or 'editorTabs' in html

    def test_nav_links_exist(self, html):
        for section in ['home', 'journey', 'work', 'skills', 'contact']:
            assert f'#{section}' in html, f"Missing nav link to #{section}"


# ─── Hero Section ─────────────────────────────────────────────

class TestHeroSection:
    def test_has_hero_section(self, html):
        assert 'id="home"' in html

    def test_has_typed_text(self, html):
        assert 'typedText' in html

    def test_has_hero_button(self, html):
        assert 'heroBtn' in html

    def test_has_social_links(self, html):
        assert 'socialLinks' in html or 'social-links' in html

    def test_has_github_link(self, html):
        assert 'github.com' in html

    def test_has_linkedin_link(self, html):
        assert 'linkedin.com' in html

    def test_has_scroll_hint(self, html):
        assert 'scrollHint' in html or 'scroll-hint' in html

    def test_has_cursor_glow(self, html):
        assert 'cursorGlow' in html

    def test_has_whiteboard_button(self, html):
        assert 'whiteboardBtn' in html


# ─── Sections ─────────────────────────────────────────────────

class TestSections:
    REQUIRED_SECTIONS = ['home', 'journey', 'work', 'skills', 'contact']

    @pytest.mark.parametrize('section_id', REQUIRED_SECTIONS)
    def test_section_exists(self, html, section_id):
        assert f'id="{section_id}"' in html

    def test_has_timeline(self, html):
        assert 'timeline' in html

    def test_has_work_cards(self, html):
        count = html.count('work-card')
        assert count >= 6, f"Expected at least 6 work-card references, found {count}"

    def test_has_skills_grid(self, html):
        assert 'skills-grid' in html or 'skillsGrid' in html

    def test_has_contact_form(self, html):
        assert 'contactForm' in html

    def test_contact_has_name_field(self, html):
        assert 'id="name"' in html

    def test_contact_has_email_field(self, html):
        assert 'id="email"' in html

    def test_contact_has_message_field(self, html):
        assert 'id="message"' in html


# ─── Try Me Button ────────────────────────────────────────────

class TestTryMeButton:
    def test_try_me_exists(self, html):
        assert 'btn-try-me' in html

    def test_try_me_links_to_render(self, html):
        assert 'mitchellsoftwareportfolio.onrender.com' in html

    def test_try_me_opens_new_tab(self, html):
        # Find the try-me link and check for target="_blank"
        pattern = r'<a[^>]*btn-try-me[^>]*>'
        match = re.search(pattern, html)
        assert match, "btn-try-me anchor tag not found"
        assert 'target="_blank"' in match.group(0)

    def test_try_me_has_noopener(self, html):
        pattern = r'<a[^>]*btn-try-me[^>]*>'
        match = re.search(pattern, html)
        assert match
        assert 'noopener' in match.group(0)

    def test_try_me_has_icon(self, html):
        # Should have a Font Awesome icon inside
        idx = html.find('btn-try-me')
        context = html[idx:idx + 200]
        assert 'fa-' in context


# ─── Analytics / Enjoyed Section ──────────────────────────────

class TestAnalyticsSection:
    STAT_IDS = ['statViews', 'statDemos', 'statPdfs', 'statVotes',
                'statUptime', 'statMemory', 'statCpu', 'statSessions']

    @pytest.mark.parametrize('stat_id', STAT_IDS)
    def test_stat_element_exists(self, html, stat_id):
        assert f'id="{stat_id}"' in html

    def test_enjoyed_button_exists(self, html):
        assert 'enjoyedBtn' in html

    def test_enjoyed_label_exists(self, html):
        assert 'enjoyedLabel' in html


# ─── Whiteboard Annotations ──────────────────────────────────

class TestWhiteboardAnnotations:
    def test_wb_overlay_exists(self, html):
        assert 'wbOverlay' in html or 'wb-overlay' in html

    def test_has_annotations(self, html):
        count = html.count('data-target=')
        assert count >= 10, f"Expected at least 10 annotations, found {count}"

    def test_annotation_targets_valid_ids(self, html):
        """Each annotation data-target should reference a real element id."""
        targets = re.findall(r'data-target="(\w+)"', html)
        for target in targets:
            assert f'id="{target}"' in html, \
                f"Annotation target '{target}' has no matching element"


# ─── Footer ───────────────────────────────────────────────────

class TestFooter:
    def test_has_footer(self, html):
        assert '<footer' in html

    def test_footer_has_copyright(self, html):
        assert '©' in html or '&copy;' in html or 'Jason Mitchell' in html


# ─── Accessibility Basics ─────────────────────────────────────

class TestAccessibility:
    def test_html_lang_attribute(self, html):
        assert 'lang="en"' in html or "lang='en'" in html

    def test_form_inputs_have_placeholders_or_labels(self, html):
        inputs = re.findall(r'<input[^>]+>', html)
        for inp in inputs:
            has_placeholder = 'placeholder=' in inp
            has_id = re.search(r'id="(\w+)"', inp)
            # Each input should have placeholder or a label referencing it
            assert has_placeholder or has_id, f"Input missing placeholder/id: {inp[:80]}"

    def test_images_have_alt_text(self, html):
        """All img tags should have alt attributes."""
        imgs = re.findall(r'<img[^>]+>', html)
        for img in imgs:
            assert 'alt=' in img, f"Image missing alt text: {img[:80]}"

    def test_links_are_not_empty(self, html):
        """Links should have content or aria-label."""
        empty_links = re.findall(r'<a[^>]*>\s*</a>', html)
        assert len(empty_links) == 0, f"Found {len(empty_links)} empty links"
