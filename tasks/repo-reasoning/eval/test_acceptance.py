from pathlib import Path


def test_documentation_file_exists_and_names_actual_code_symbols():
    note = Path("docs/config-flow.md")
    assert note.is_file(), "create docs/config-flow.md"
    text = note.read_text(encoding="utf8").lower()
    for required in ("load_service_config", "service_timeout_seconds", "service.json", "30", "config.py"):
        assert required in text, f"documentation must explain {required}"


def test_documentation_states_precedence():
    text = Path("docs/config-flow.md").read_text(encoding="utf8").lower()
    assert "environment" in text and ("override" in text or "precedence" in text)
