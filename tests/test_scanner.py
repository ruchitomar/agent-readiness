from pathlib import Path

from agent_readiness.scanner import scan_repository


def _finding(findings, dimension: str):
    return next(f for f in findings if f.dimension == dimension)


def test_empty_repository_scores_low(tmp_path: Path) -> None:
    findings = scan_repository(tmp_path)

    context = _finding(findings, "Repository Context")
    architecture = _finding(findings, "Architecture")
    testing = _finding(findings, "Testing")
    agent_instructions = _finding(findings, "Agent Instructions")

    assert context.score == 0
    assert context.status == "FAIL"

    assert architecture.score == 0
    assert architecture.status == "FAIL"

    assert testing.score == 0
    assert testing.status == "FAIL"

    assert agent_instructions.score == 0
    assert agent_instructions.status == "FAIL"


def test_repository_context_detects_standard_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text("Contribute", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache-2.0", encoding="utf-8")

    findings = scan_repository(tmp_path)
    context = _finding(findings, "Repository Context")

    assert context.score == 100
    assert context.status == "PASS"
    assert "README.md found" in context.evidence
    assert "CONTRIBUTING.md found" in context.evidence
    assert "LICENSE found" in context.evidence
    assert context.recommendations == []


def test_architecture_detects_architecture_document(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()

    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
    (docs / "ARCHITECTURE.md").write_text(
        "# Architecture",
        encoding="utf-8",
    )

    findings = scan_repository(tmp_path)
    architecture = _finding(findings, "Architecture")

    assert architecture.score == 100
    assert architecture.status == "PASS"


def test_testing_detects_tests_and_ci(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    workflows = tmp_path / ".github" / "workflows"

    tests.mkdir()
    workflows.mkdir(parents=True)

    (workflows / "test.yml").write_text(
        "name: test",
        encoding="utf-8",
    )

    findings = scan_repository(tmp_path)
    testing = _finding(findings, "Testing")

    assert testing.score == 100
    assert testing.status == "PASS"


def test_agent_instruction_file_scores_pass(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(
        "# Agent Instructions",
        encoding="utf-8",
    )

    findings = scan_repository(tmp_path)
    instructions = _finding(findings, "Agent Instructions")

    assert instructions.score == 100
    assert instructions.status == "PASS"
    assert any(
        "AGENTS.md" in evidence
        for evidence in instructions.evidence
    )


def test_mcp_configuration_is_detected(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text(
        "{}",
        encoding="utf-8",
    )

    findings = scan_repository(tmp_path)
    mcp = _finding(findings, "MCP / Tool Governance")

    assert mcp.score == 60
    assert mcp.status == "WARN"
    assert any(
        ".mcp.json" in evidence
        for evidence in mcp.evidence
    )


def test_human_review_detects_codeowners_ci_and_contributing(
    tmp_path: Path,
) -> None:
    github = tmp_path / ".github"
    workflows = github / "workflows"

    workflows.mkdir(parents=True)

    (github / "CODEOWNERS").write_text(
        "* @engineering-team",
        encoding="utf-8",
    )
    (tmp_path / "CONTRIBUTING.md").write_text(
        "Review required",
        encoding="utf-8",
    )
    (workflows / "checks.yml").write_text(
        "name: checks",
        encoding="utf-8",
    )

    findings = scan_repository(tmp_path)
    human_review = _finding(findings, "Human Review")

    assert human_review.score == 100
    assert human_review.status == "PASS"


def test_security_detects_policy_gitignore_codeowners_and_ci(
    tmp_path: Path,
) -> None:
    github = tmp_path / ".github"
    workflows = github / "workflows"

    workflows.mkdir(parents=True)

    (tmp_path / "SECURITY.md").write_text(
        "# Security",
        encoding="utf-8",
    )
    (tmp_path / ".gitignore").write_text(
        ".env",
        encoding="utf-8",
    )
    (github / "CODEOWNERS").write_text(
        "* @engineering-team",
        encoding="utf-8",
    )
    (workflows / "security.yml").write_text(
        "name: security",
        encoding="utf-8",
    )

    findings = scan_repository(tmp_path)
    security = _finding(findings, "Security")

    assert security.score == 100
    assert security.status == "PASS"
