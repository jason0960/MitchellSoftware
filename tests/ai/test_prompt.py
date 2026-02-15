"""
Tests for the AI prompt module.
"""
import json
import os
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from ai.prompt import load_system_prompt


# ═══════════════════════════════════════════════════════════════
# Core Loading
# ═══════════════════════════════════════════════════════════════

def test_load_system_prompt_returns_string():
    """load_system_prompt() should return a non-empty string."""
    prompt = load_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 500


def test_prompt_contains_name():
    """Prompt should contain Jason's name."""
    prompt = load_system_prompt()
    assert 'Jason Mitchell' in prompt


def test_prompt_contains_skills():
    """Prompt should contain technical skills sections."""
    prompt = load_system_prompt()
    assert 'TECHNICAL SKILLS' in prompt
    assert 'Java' in prompt
    assert 'React' in prompt


def test_custom_profile_path():
    """load_system_prompt() should accept a custom profile path."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    prompt = load_system_prompt(profile_path=profile_path)
    assert 'Jason Mitchell' in prompt


def test_invalid_profile_path_raises():
    """load_system_prompt() should raise on bad path."""
    with pytest.raises(FileNotFoundError):
        load_system_prompt(profile_path='/nonexistent/path.json')


# ═══════════════════════════════════════════════════════════════
# Prompt Sections
# ═══════════════════════════════════════════════════════════════

def test_prompt_contains_guardrails():
    """Prompt should contain safety guardrails."""
    prompt = load_system_prompt()
    assert 'SAFETY GUARDRAILS' in prompt
    assert 'NEVER share personal information' in prompt
    assert 'reprogrammed' in prompt.lower()


def test_prompt_contains_career_timeline():
    """Prompt should include career history."""
    prompt = load_system_prompt()
    assert 'CAREER TIMELINE' in prompt
    assert 'Home Depot' in prompt


def test_prompt_contains_strengths_and_growth():
    """Prompt should include honest self-assessment."""
    prompt = load_system_prompt()
    assert 'STRENGTHS' in prompt
    assert 'AREAS FOR GROWTH' in prompt


def test_prompt_contains_personality_section():
    """Prompt should include personality & tone instructions."""
    prompt = load_system_prompt()
    assert 'PERSONALITY' in prompt
    assert 'Professional' in prompt


def test_prompt_contains_key_contributions():
    """Prompt should list key contributions."""
    prompt = load_system_prompt()
    assert 'KEY CONTRIBUTIONS' in prompt


def test_prompt_contains_portfolio_projects():
    """Prompt should reference portfolio projects."""
    prompt = load_system_prompt()
    assert 'PORTFOLIO PROJECTS' in prompt


def test_prompt_contains_contact_info():
    """Prompt should include email, GitHub, and LinkedIn."""
    prompt = load_system_prompt()
    assert 'jasonmitchell096@gmail.com' in prompt
    assert 'github.com' in prompt
    assert 'linkedin.com' in prompt


def test_prompt_contains_what_looking_for():
    """Prompt should include what Jason is looking for."""
    prompt = load_system_prompt()
    assert 'WHAT JASON IS LOOKING FOR' in prompt


def test_prompt_third_person_instruction():
    """Prompt should instruct using third person."""
    prompt = load_system_prompt()
    assert 'third person' in prompt.lower()


def test_prompt_salary_redirect():
    """Prompt should redirect salary questions."""
    prompt = load_system_prompt()
    assert 'salary' in prompt.lower()


def test_prompt_honest_assessment_instruction():
    """Prompt should instruct honest fit assessment."""
    prompt = load_system_prompt()
    assert 'honest' in prompt.lower()
    assert 'gaps' in prompt.lower()


# ═══════════════════════════════════════════════════════════════
# Guardrail Details
# ═══════════════════════════════════════════════════════════════

def test_guardrail_no_personal_info():
    """Guardrails should prevent sharing personal info beyond listed contacts."""
    prompt = load_system_prompt()
    assert 'phone' in prompt.lower() or 'address' in prompt.lower()


def test_guardrail_no_company_bashing():
    """Guardrails should prevent negative talk about employers."""
    prompt = load_system_prompt()
    assert 'negatively' in prompt.lower()


def test_guardrail_anti_jailbreak():
    """Guardrails should resist prompt injection."""
    prompt = load_system_prompt()
    assert 'override' in prompt.lower() or 'reprogrammed' in prompt.lower()


def test_guardrail_no_controversial_topics():
    """Guardrails should redirect political/religious topics."""
    prompt = load_system_prompt()
    assert 'political' in prompt.lower() or 'controversial' in prompt.lower()


def test_guardrail_no_unrelated_tasks():
    """Guardrails should prevent code generation or off-topic tasks."""
    prompt = load_system_prompt()
    assert 'unrelated' in prompt.lower()


# ═══════════════════════════════════════════════════════════════
# Profile JSON Schema
# ═══════════════════════════════════════════════════════════════

def test_profile_json_valid():
    """jason_profile.json should be valid JSON with required keys."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    with open(profile_path) as f:
        profile = json.load(f)

    required_keys = ['name', 'title', 'summary', 'career_timeline',
                     'key_contributions', 'technical_skills',
                     'portfolio_projects', 'honest_self_assessment']
    for key in required_keys:
        assert key in profile, f'Missing key: {key}'


def test_profile_career_timeline_structure():
    """Each career entry should have role, company, type, description."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    with open(profile_path) as f:
        profile = json.load(f)

    assert len(profile['career_timeline']) > 0
    for entry in profile['career_timeline']:
        assert 'role' in entry
        assert 'company' in entry
        assert 'type' in entry
        assert 'description' in entry


def test_profile_technical_skills_non_empty():
    """Technical skills should have at least one category with items."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    with open(profile_path) as f:
        profile = json.load(f)

    skills = profile['technical_skills']
    assert len(skills) > 0
    for category, items in skills.items():
        assert isinstance(items, list)
        assert len(items) > 0, f'Empty skill category: {category}'


def test_profile_contributions_have_technologies():
    """Each key contribution should reference technologies used."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    with open(profile_path) as f:
        profile = json.load(f)

    for contrib in profile['key_contributions']:
        assert 'area' in contrib
        assert 'detail' in contrib
        assert 'technologies' in contrib
        assert isinstance(contrib['technologies'], list)


def test_profile_honest_assessment_has_both():
    """Self-assessment should have both strengths and growth areas."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    with open(profile_path) as f:
        profile = json.load(f)

    assessment = profile['honest_self_assessment']
    assert 'strengths' in assessment
    assert 'areas_for_growth' in assessment
    assert len(assessment['strengths']) > 0
    assert len(assessment['areas_for_growth']) > 0


def test_profile_portfolio_projects_structure():
    """Portfolio projects should have name, description, technologies."""
    profile_path = os.path.join(ROOT_DIR, 'ai', 'jason_profile.json')
    with open(profile_path) as f:
        profile = json.load(f)

    for proj in profile['portfolio_projects']:
        assert 'name' in proj
        assert 'description' in proj
        assert 'technologies' in proj


# ═══════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════

def test_malformed_json_raises():
    """A file with invalid JSON should raise an error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{bad json')
        f.flush()
        tmp_path = f.name
    try:
        with pytest.raises(json.JSONDecodeError):
            load_system_prompt(profile_path=tmp_path)
    finally:
        os.unlink(tmp_path)


def test_missing_key_in_profile_raises():
    """A profile missing required keys should raise a KeyError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({'name': 'Test'}, f)  # missing most keys
        f.flush()
        tmp_path = f.name
    try:
        with pytest.raises(KeyError):
            load_system_prompt(profile_path=tmp_path)
    finally:
        os.unlink(tmp_path)
