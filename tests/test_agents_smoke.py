"""
Smoke tests for the CrewAI agent layer — validates that all imports work,
tools are callable, and the dry-run campaign can be imported without crashing.

These tests do NOT require Docker to be running (no HTTP calls).
They validate the Python module structure and tool definitions.
"""

import os

# Force dry run so no HTTP calls are made
os.environ["DRY_RUN"] = "true"


def test_payload_library_imports():
    from agents.tools.payload_library import get_payloads

    assert callable(get_payloads)


def test_payload_library_returns_all():
    from agents.tools.payload_library import PAYLOADS

    # Just verify the dict has expected keys
    assert "direct_injection" in PAYLOADS
    assert "privesc_tasks" in PAYLOADS
    assert "webagent_injection" in PAYLOADS


def test_mitre_mapper_imports():
    from agents.tools.mitre_mapper import ATLAS_TECHNIQUES

    assert "AML.T0054" in ATLAS_TECHNIQUES
    assert "AML.T0040" in ATLAS_TECHNIQUES


def test_mitre_mapper_maps_injection():
    from agents.tools.mitre_mapper import ATLAS_TECHNIQUES

    # The mapper's keyword list for AML.T0054 should include "prompt injection"
    technique = ATLAS_TECHNIQUES["AML.T0054"]
    assert any("injection" in kw for kw in technique["keywords"])


def test_obsidian_writer_imports():
    from agents.tools.obsidian_writer import write_finding, write_campaign_report

    assert callable(write_finding)
    assert callable(write_campaign_report)


def test_http_client_dry_run(monkeypatch):
    """In DRY_RUN mode, http_client tools should not make real HTTP requests."""
    monkeypatch.setenv("DRY_RUN", "true")
    # Re-import after monkeypatch
    import importlib
    import agents.tools.http_client as hc

    importlib.reload(hc)
    assert hc.DRY_RUN is True


def test_campaign_imports():
    """campaign.py should import without errors."""
    import agents.campaign

    assert hasattr(agents.campaign, "run_campaign")
    assert hasattr(agents.campaign, "TARGET_CONFIGS")


def test_crew_imports():
    """crew.py should import without errors and expose build_crew."""
    import agents.crew

    assert hasattr(agents.crew, "build_crew")
    assert callable(agents.crew.build_crew)


def test_all_roles_import():
    """All 7 agent role modules should import cleanly."""
    from agents.roles.recon_agent import recon_agent, recon_task
    from agents.roles.prompt_injection_agent import injection_agent, injection_task
    from agents.roles.jailbreak_agent import jailbreak_agent, jailbreak_task
    from agents.roles.data_extraction_agent import extraction_agent, extraction_task
    from agents.roles.privilege_escalation_agent import privesc_agent, privesc_task
    from agents.roles.webattack_agent import webattack_agent, webattack_task
    from agents.roles.report_agent import report_agent, report_task

    for agent in [
        recon_agent,
        injection_agent,
        jailbreak_agent,
        extraction_agent,
        privesc_agent,
        webattack_agent,
        report_agent,
    ]:
        assert agent is not None

    for task in [
        recon_task,
        injection_task,
        jailbreak_task,
        extraction_task,
        privesc_task,
        webattack_task,
        report_task,
    ]:
        assert task is not None
