"""Tests for the persona system."""
from roastme.personas.base import PERSONAS, get_persona


def test_all_personas_exist():
    expected = {
        "disappointed_mentor", "chaos_goblin", "senior_dev_karen",
        "standup_comedian", "drill_sergeant", "therapist",
    }
    assert set(PERSONAS.keys()) == expected


def test_persona_has_required_fields():
    for pid, persona in PERSONAS.items():
        assert persona.name, f"{pid} missing name"
        assert persona.emoji, f"{pid} missing emoji"
        assert persona.system_prompt, f"{pid} missing system_prompt"
        assert len(persona.roast_prefixes) > 0, f"{pid} missing prefixes"
        assert len(persona.roast_suffixes) > 0, f"{pid} missing suffixes"


def test_get_persona_valid():
    persona = get_persona("chaos_goblin")
    assert persona.name == "Chaos Goblin"


def test_get_persona_invalid():
    with pytest.raises(ValueError):
        get_persona("nonexistent_persona")
