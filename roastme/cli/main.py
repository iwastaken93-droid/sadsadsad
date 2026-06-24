"""CLI entry point — bring the heat to your terminal."""
from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from roastme.analyzer.engine import CodeAnalyzer
from roastme.config import RoastConfig
from roastme.reviewer.engine import ReviewEngine

console = Console()


BANNER = r"""
[bold red]  ____            _    _____                [/bold red]
[bold red] |  _ \ ___  __ _| |_ /__   \___  ___  ___  [/bold red]
[bold red] | |_) / _ \/ _` | __| / /\/ _ \/ __|/ _ \ [/bold red]
[bold red] |  _ <  __/ (_| | |_ / / |  __/\__ \  __/ [/bold red]
[bold red] |_| \_\___|\__,_|\__| \/   \___||___/\___| [/bold red]
[bold yellow]        🔥 Your code is about to get roasted 🔥[/bold yellow]
"""


@click.group()
@click.option("--config", is_flag=True, help="Open configuration")
def cli(config):
    """RoastMe — AI code reviewer that absolutely roasts your code."""
    if config:
        _configure()


def _configure():
    """Interactive configuration."""
    console.print(Panel("🔧 [bold]RoastMe Configuration[/bold]", border_style="yellow"))
    cfg = RoastConfig.load()

    api_key = click.prompt("API Key", default=cfg.api_key, hide_input=True)
    api_base = click.prompt("API Base URL", default=cfg.api_base)
    model = click.prompt("Model", default=cfg.model)
    roast_level = click.prompt(
        "Roast Level", type=click.Choice(["mild", "medium", "savage", "nuclear"]), default=cfg.roast_level
    )
    persona = click.prompt(
        "Persona",
        type=click.Choice([
            "disappointed_mentor", "chaos_goblin", "senior_dev_karen",
            "standup_comedian", "drill_sergeant", "therapist",
        ]),
        default=cfg.persona,
    )

    cfg.api_key = api_key
    cfg.api_base = api_base
    cfg.model = model
    cfg.roast_level = roast_level
    cfg.persona = persona
    cfg.save()
    console.print("[green]✅ Configuration saved![/green]")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--persona", "-p", default=None, help="Override persona")
@click.option("--level", "-l", default=None, type=click.Choice(["mild", "medium", "savage", "nuclear"]))
def roast(file_path, persona, level):
    """Roast a single file."""
    console.print(BANNER)
    cfg = RoastConfig.load()
    if persona:
        cfg.persona = persona
    if level:
        cfg.roast_level = level

    if not cfg.api_key:
        console.print("[red]❌ No API key configured. Run `roastme --config` first.[/red]")
        sys.exit(1)

    source = Path(file_path).read_text()
    analyzer = CodeAnalyzer()
    analysis = analyzer.analyze(file_path, source)

    console.print(f"\n[bold cyan]📁 Analyzing:[/bold cyan] {file_path}")
    console.print(f"[dim]{analysis.summary}[/dim]\n")

    engine = ReviewEngine(cfg)
    result = engine.review(file_path, source, analysis)

    _display_result(result, source)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def analyze(file_path):
    """Static analysis only (no AI roast)."""
    console.print(BANNER)
    source = Path(file_path).read_text()
    analyzer = CodeAnalyzer()
    analysis = analyzer.analyze(file_path, source)

    console.print(f"\n[bold cyan]📁 Analysis:[/bold cyan] {file_path}")
    console.print(f"[dim]{analysis.summary}[/dim]\n")

    if not analysis.findings:
        console.print("[green]No issues found. Suspiciously clean...[/green]")
        return

    table = Table(title="Findings", show_lines=True)
    table.add_column("Line", style="bold", width=6)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=14)
    table.add_column("Issue", width=40)
    table.add_column("Roast Hint", width=40)

    for f in analysis.findings:
        sev_color = {"critical": "red", "warning": "yellow", "info": "blue"}.get(f.severity.value, "white")
        table.add_row(
            str(f.line),
            f"[{sev_color}]{f.severity.value.upper()}[/{sev_color}]",
            f.category.value,
            f.message[:50],
            f.roast_hint[:50] if f.roast_hint else "",
        )

    console.print(table)


@cli.command()
@click.option("--port", "-p", default=8137, help="Port to run on")
def serve(port):
    """Start the RoastMe web UI server."""
    console.print(f"[bold red]🔥 Starting RoastMe server on http://localhost:{port}[/bold red]")
    import uvicorn
    from roastme.web.app import app
    uvicorn.run(app, host="127.0.0.1", port=port)


def _display_result(result, source: str):
    """Display a review result with rich formatting."""
    # Shame score
    score_color = "green" if result.shame_score < 20 else "yellow" if result.shame_score < 50 else "red"
    console.print(Panel(
        f"[bold {score_color}]Shame Score: {result.shame_score}/100[/{score_color}]",
        title=f"{result.persona_name} says:",
        border_style=score_color,
    ))

    # Overall roast
    console.print(Panel(
        result.overall_roast,
        title="🔥 [bold red]The Roast[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))

    # Line roasts
    if result.line_roasts:
        table = Table(title="🎯 Line-by-Line Burns", show_lines=True)
        table.add_column("Line", width=6, style="bold")
        table.add_column("Code", width=40)
        table.add_column("Burn", width=50)
        table.add_column("Fix", width=40, style="green")

        for lr in result.line_roasts:
            table.add_row(
                str(lr.line),
                lr.code_snippet[:40],
                lr.roast[:60],
                lr.suggestion[:50],
            )
        console.print(table)

    # Suggestions
    if result.refactoring_suggestions:
        console.print("\n[bold green]💡 Refactoring Suggestions:[/bold green]")
        for i, s in enumerate(result.refactoring_suggestions, 1):
            console.print(f"  {i}. {s}")


if __name__ == "__main__":
    cli()
