from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    help="Assess how ready a software repository is for AI-assisted and agentic engineering."
)

console = Console()


DIMENSIONS = [
    ("Repository Context", 82, "PASS"),
    ("Architecture", 74, "WARN"),
    ("Testing", 91, "PASS"),
    ("Security", 78, "WARN"),
    ("Secrets Protection", 100, "PASS"),
    ("MCP / Tool Governance", 45, "WARN"),
    ("Agent Instructions", 85, "PASS"),
    ("Human Review", 70, "WARN"),
    ("Observability", 55, "WARN"),
    ("Evidence", 80, "PASS"),
]


def _verdict(score: int) -> str:
    if score >= 85:
        return "READY"
    if score >= 70:
        return "READY WITH CONDITIONS"
    return "NOT READY"


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
    )
) -> None:
    """
    Assess a repository and display its current readiness score.

    V0.1 uses a starter scoring model. Repository evidence detection
    will replace these baseline values as the project evolves.
    """

    console.print()
    console.print("[bold]Agent Readiness[/bold]")
    console.print(f"[dim]Repository: {path}[/dim]")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    scores = []

    for dimension, score, status in DIMENSIONS:
        scores.append(score)
        table.add_row(dimension, str(score), status)

    console.print(table)

    overall = round(sum(scores) / len(scores))

    console.print()
    console.print(f"[bold]Overall Readiness:[/bold] {overall} / 100")
    console.print(f"[bold]Verdict:[/bold] {_verdict(overall)}")
    console.print()

    console.print("[bold]Top recommendations[/bold]")
    console.print("1. Define approved MCP and tool integrations.")
    console.print("2. Add explicit AI-generated-code review guidance.")
    console.print("3. Improve architecture context for cross-module changes.")


@app.command()
def explain(
    dimension: str = typer.Argument(
        ...,
        help="Readiness dimension to explain.",
    )
) -> None:
    """
    Explain what a readiness dimension represents.
    """

    console.print(
        f"[bold]{dimension}[/bold]\\n\\n"
        "Detailed evidence-backed explanations are planned for V0.1."
    )


@app.command()
def version() -> None:
    """
    Show the Agent Readiness CLI version.
    """

    console.print("Agent Readiness 0.1.0")


if __name__ == "__main__":
    app()
