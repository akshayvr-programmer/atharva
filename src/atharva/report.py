from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

console = Console(theme=Theme({"markdown.code": "bold cyan"}))


COLORS = {
    "OK": "green", "WA": "red", "TLE": "yellow",
    "RE": "magenta", "NO ANSWER": "blue",
}

def badge(name, status, t):
    console.print(Text.assemble(
        (f" {status} ", f"bold reverse {COLORS[status]}"),
        f"  {name}  ",
        (f"{t:.2f}s", "dim"),
    ))

def lines_of(s):
    return s.rstrip("\n").split("\n") if s.strip() else []

def diff(got, exp):
    g, e = lines_of(got), lines_of(exp)
    table = Table(box=box.SIMPLE, header_style="bold")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Expected")
    table.add_column("Yours")

    rows = []
    for i in range(max(len(g), len(e))):
        et_tokens = e[i].split() if i < len(e) else []
        gt_tokens = g[i].split() if i < len(g) else []
        et, gt, bad_line = Text(), Text(), False
        for j in range(max(len(et_tokens), len(gt_tokens))):
            a = et_tokens[j] if j < len(et_tokens) else None
            b = gt_tokens[j] if j < len(gt_tokens) else None
            bad = a != b
            bad_line |= bad
            if a is not None:
                et.append(a + " ", style="bold green" if bad else "")
            if b is not None:
                gt.append(b + " ", style="bold red" if bad else "")
            elif bad:
                gt.append("∅ ", style="bold red")
        rows.append((i + 1, et, gt, bad_line))

    if len(rows) > 40:
        rows = [r for r in rows if r[3]][:20]
    for num, et, gt, _ in rows:
        table.add_row(str(num), et, gt)
    console.print(table)

def stderr_box(err):
    if err.strip():
        console.print(Text(err.rstrip()[-1500:], style="dim"))

def summary(passed, total, unchecked=0):
    style = "bold green" if passed == total else "bold red"
    msg = f"\n{passed}/{total} passed"
    if unchecked:
        msg += f", {unchecked} unchecked"
    console.print(Text(msg, style=style))
