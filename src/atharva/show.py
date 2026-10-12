from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from .report import console

def heading(name):
    console.print()
    console.print(Rule(f"[bold cyan]{name}[/]", style="cyan dim", align="left"))

def sample_box(text, title):
    return Panel(Text(text.rstrip()), title=f"[dim]{title}[/]",
                 title_align="left", border_style="dim", box=box.ROUNDED)

def show_statement(s):
    head = Text.assemble(
        (s["title"], "bold"), "\n",
        (f"time {s['time']}  ·  memory {s['memory']}", "dim"),
    )
    console.print(Panel(head, border_style="cyan", box=box.ROUNDED, padding=(1, 2)))
    console.print(Markdown(s["legend"]))

    heading("Input")
    console.print(Markdown(s["input"]))
    heading("Output")
    console.print(Markdown(s["output"]))

    for i, (a, b) in enumerate(s["samples"], start=1):
        heading(f"Sample {i}")
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        grid.add_row(sample_box(a, "input"), sample_box(b, "output"))
        console.print(grid)

    if s["note"]:
        heading("Note")
        console.print(Markdown(s["note"]))
