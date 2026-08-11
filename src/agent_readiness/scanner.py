from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    dimension: str
    score: int
    status: str
    evidence: list[str]
    recommendations: list[str]


AGENT_INSTRUCTION_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".cursor/rules",
    ".cursorrules",
)

MCP_FILES = (
    ".mcp.json",
    "mcp.json",
    ".vscode/mcp.json",
)

ARCHITECTURE_FILES = (
    "ARCHITECTURE.md",
    "docs/ARCHITECTURE.md",
    "docs/architecture.md",
)

SECURITY_FILES = (
    "SECURITY.md",
    ".github/SECURITY.md",
)

CODEOWNERS_FILES = (
    "CODEOWNERS",
    ".github/CODEOWNERS",
    "docs/CODEOWNERS",
)

CI_FILES = (
    ".github/workflows",
    ".gitlab-ci.yml",
    "Jenkinsfile",
)


def _exists_any(root: Path, candidates: Iterable[str]) -> list[str]:
    found: list[str] = []

    for candidate in candidates:
        path = root / candidate
        if path.exists():
            found.append(candidate)

    return found


def _has_tests(root: Path) -> list[str]:
    candidates = (
        "tests",
        "test",
        "__tests__",
        "src/test",
        "src/tests",
    )
    return _exists_any(root, candidates)


def _score(
    dimension: str,
    checks: list[tuple[bool, int, str]],
    recommendations: list[str],
) -> Finding:
    score = sum(points for passed, points, _ in checks if passed)
    evidence = [message for passed, _, message in checks if passed]

    if score >= 80:
        status = "PASS"
    elif score >= 50:
        status = "WARN"
    else:
        status = "FAIL"

    return Finding(
        dimension=dimension,
        score=min(score, 100),
        status=status,
        evidence=evidence,
        recommendations=recommendations if score < 80 else [],
    )


def scan_repository(root: Path) -> list[Finding]:
    root = root.resolve()

    readme = (root / "README.md").exists()
    contributing = (root / "CONTRIBUTING.md").exists()
    license_file = (root / "LICENSE").exists()

    architecture = _exists_any(root, ARCHITECTURE_FILES)
    tests = _has_tests(root)
    security = _exists_any(root, SECURITY_FILES)
    codeowners = _exists_any(root, CODEOWNERS_FILES)
    ci = _exists_any(root, CI_FILES)
    agent_instructions = _exists_any(root, AGENT_INSTRUCTION_FILES)
    mcp = _exists_any(root, MCP_FILES)

    gitignore = (root / ".gitignore").exists()

    findings = [
        _score(
            "Repository Context",
            [
                (readme, 60, "README.md found"),
                (contributing, 20, "CONTRIBUTING.md found"),
                (license_file, 20, "LICENSE found"),
            ],
            [
                "Add a clear README describing repository purpose and development workflow.",
                "Add CONTRIBUTING.md for repeatable contributor guidance.",
                "Include an explicit open-source or internal-use license where appropriate.",
            ],
        ),
        _score(
            "Architecture",
            [
                (bool(architecture), 70, f"Architecture guidance found: {', '.join(architecture)}"),
                (readme, 30, "README provides baseline repository context"),
            ],
            [
                "Add ARCHITECTURE.md or docs/ARCHITECTURE.md.",
                "Document service boundaries, dependencies, and major design constraints.",
            ],
        ),
        _score(
            "Testing",
            [
                (bool(tests), 70, f"Test location found: {', '.join(tests)}"),
                (bool(ci), 30, f"CI configuration found: {', '.join(ci)}"),
            ],
            [
                "Add automated tests.",
                "Run tests in CI so agent-generated changes are verified automatically.",
            ],
        ),
        _score(
            "Security",
            [
                (bool(security), 40, f"Security policy found: {', '.join(security)}"),
                (gitignore, 20, ".gitignore found"),
                (bool(codeowners), 20, f"CODEOWNERS found: {', '.join(codeowners)}"),
                (bool(ci), 20, "CI configuration available for security/quality checks"),
            ],
            [
                "Add SECURITY.md with vulnerability reporting guidance.",
                "Add CODEOWNERS for sensitive or critical paths.",
                "Wire security and quality checks into CI.",
            ],
        ),
        _score(
            "Secrets Protection",
            [
                (gitignore, 50, ".gitignore found"),
                (bool(ci), 25, "CI exists and can host secret-scanning checks"),
                (bool(security), 25, "Security policy found"),
            ],
            [
                "Add or review .gitignore patterns for secrets and local credentials.",
                "Enable secret scanning in CI or repository settings.",
                "Document how developers should handle local credentials.",
            ],
        ),
        _score(
            "Agent Instructions",
            [
                (
                    bool(agent_instructions),
                    100,
                    f"Agent instruction surface found: {', '.join(agent_instructions)}",
                ),
            ],
            [
                "Add AGENTS.md or a supported client-specific instruction file.",
                "Document build, test, architecture, and safety expectations for coding agents.",
            ],
        ),
        _score(
            "MCP / Tool Governance",
            [
                (bool(mcp), 60, f"MCP configuration found: {', '.join(mcp)}"),
                (bool(security), 20, "Security policy provides a governance surface"),
                (bool(codeowners), 20, "CODEOWNERS supports review of integration changes"),
            ],
            [
                "Document approved MCP/tool integrations.",
                "Apply least privilege to connected tools.",
                "Require review for MCP or tool-configuration changes.",
            ],
        ),
        _score(
            "Human Review",
            [
                (bool(codeowners), 50, f"CODEOWNERS found: {', '.join(codeowners)}"),
                (bool(ci), 30, "CI supports automated pre-review validation"),
                (contributing, 20, "Contributor guidance found"),
            ],
            [
                "Add CODEOWNERS or equivalent review ownership.",
                "Document review expectations for AI-generated changes.",
                "Require automated validation before merge.",
            ],
        ),
        _score(
            "Observability",
            [
                (bool(ci), 50, "CI provides an initial operational feedback surface"),
                (readme, 20, "Repository documentation exists"),
            ],
            [
                "Document application logging and observability expectations.",
                "Add operational or telemetry guidance for production repositories.",
            ],
        ),
        _score(
            "Evidence",
            [
                (bool(ci), 40, "CI produces repeatable build/test evidence"),
                (bool(codeowners), 20, "Review ownership is documented"),
                (bool(agent_instructions), 20, "Agent instructions are repository-owned"),
                (bool(architecture), 20, "Architecture guidance is repository-owned"),
            ],
            [
                "Preserve CI results and review evidence.",
                "Keep agent instructions and architecture guidance version controlled.",
                "Add machine-readable readiness reports in a later Agent Readiness release.",
            ],
        ),
    ]

    return findings
