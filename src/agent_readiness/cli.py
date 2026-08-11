from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agent_readiness.scanner import Finding, scan_repository

app = typer.Typer(
    help="Assess how ready a software repository is for AI-assisted and agentic engineering."
)

console = Console()


def _verdict(score: int) -> str:
    if score >= 85:
        return "READY"
    if score >= 70:
        return "READY WITH CONDITIONS"
    return "NOT READY"


def _overall_score(findings: list[Finding]) -> int:
    if not findings:
        return 0

    return round(sum(finding.score for finding in findings) / len(findings))


def _status_style(status: str) -> str:
    if status == "PASS":
        return "green"
    if status == "WARN":
        return "yellow"
    return "red"


@app.command()
def assess(
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Repository directory to assess.",
    ),
    details: bool = typer.Option(
        False,
        "--details",
        "-d",
        help="Show evidence and recommendations for each readiness dimension.",
    ),
) -> None:
    """
    Assess a repository and display its Agent Readiness score.
    """

    findings = scan_repository(path)
    overall = _overall_score(findings)

    console.print()
    console.print("[bold]Agent Readiness[/bold]")
    console.print(f"[dim]Repository: {path}[/dim]")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    for finding in findings:
        style = _status_style(finding.status)

        table.add_row(
            finding.dimension,
            str(finding.score),
            f"[{style}]{finding.status}[/{style}]",
        )

    console.print(table)

    console.print()
    console.print(f"[bold]Overall Readiness:[/bold] {overall} / 100")
    console.print(f"[bold]Verdict:[/bold] {_verdict(overall)}")

    recommendations: list[str] = []

    for finding in findings:
        recommendations.extend(finding.recommendations)

    if recommendations:
        console.print()
        console.print("[bold]Top recommendations[/bold]")

        for index, recommendation in enumerate(recommendations[:5], start=1):
            console.print(f"{index}. {recommendation}")

    if details:
        console.print()
        console.rule("Readiness Evidence")

        for finding in findings:
            console.print()
            console.print(
                f"[bold]{finding.dimension}[/bold] "
                f"({finding.score}/100 — {finding.status})"
            )

            if finding.evidence:
                console.print("[bold]Evidence[/bold]")
                for evidence in finding.evidence:
                    console.print(f"  • {evidence}")
            else:
                console.print("[dim]No positive repository evidence detected.[/dim]")

            if finding.recommendations:
                console.print("[bold]Recommendations[/bold]")
                for recommendation in finding.recommendations:
                    console.print(f"  • {recommendation}")


@app.command()
def explain(
    dimension: str = typer.Argument(
        ...,
        help="Readiness dimension to explain.",
    )
) -> None:
    """
    Explain a readiness dimension using the current repository.
    """

    findings = scan_repository(Path("."))

    normalized = dimension.strip().lower()

    matching = [
        finding
        for finding in findings
        if normalized in finding.dimension.lower()
    ]

    if not matching:
        console.print(
            f"[red]Unknown readiness dimension:[/red] {dimension}"
        )
        console.print()
        console.print("Available dimensions:")

        for finding in findings:
            console.print(f"  • {finding.dimension}")

        raise typer.Exit(code=1)

    finding = matching[0]

    console.print()
    console.print(f"[bold]{finding.dimension}[/bold]")
    console.print(f"Score: {finding.score}/100")
    console.print(f"Status: {finding.status}")

    console.print()

    if finding.evidence:
        console.print("[bold]Evidence[/bold]")
        for evidence in finding.evidence:
            console.print(f"  • {evidence}")
    else:
        console.print("[dim]No positive repository evidence detected.[/dim]")

    if finding.recommendations:
        console.print()
        console.print("[bold]Recommendations[/bold]")
        for recommendation in finding.recommendations:
            console.print(f"  • {recommendation}")


@app.command()
def version() -> None:
    """
    Show the Agent Readiness CLI version.
    """

    console.print("Agent Readiness 0.1.0")


if __name__ == "__main__":
    app()
