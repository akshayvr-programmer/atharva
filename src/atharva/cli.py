import argparse, os
from .browser import open_cf
from .watch import get_handle, get_sub_id, watch
from .langs import LANGS
from pathlib import Path
from .fetch import split_code, get_page, save_samples
from rich.console import Console
from rich.markdown import Markdown
from .fetch import statement_md
from .runner import run_tests
from .custom import add_test
from .fetch import statement_parts, statement_md
from .fetch import split_code, get_page, save_samples, statement_parts, statement_md
from .show import show_statement
from .report import console
from importlib.metadata import version
from rich_argparse import RawDescriptionRichHelpFormatter as Fmt
import sys,os,argparse

EXAMPLES = """\
typical flow:
  cfx login                 one-time browser login
  cfx fetch 1878E           statement + samples into ./1878E/
  cfx add 1878E             paste a custom test
  cfx test 1878E ans.cpp    run all tests, see diffs
  cfx emit 1878E ans.cpp    submit and watch the verdict
"""
def login():
    p, ctx = open_cf()
    page = ctx.new_page()
    page.goto("https://codeforces.com/enter")
    print("Log in to Codeforces in the browser window...")
    page.wait_for_selector("#header a[href^='/profile/']", timeout=300_000)
    print(f"Logged in as {get_handle(page)}. You're all set.")
    ctx.close(); p.stop()

def emit(problem, src):
    src = Path(src)
    if not src.exists():
        src = Path(problem.upper()) / src.name
    lang = LANGS[src.suffix]["id"]

    p, ctx = open_cf()
    page = ctx.new_page()
    page.goto("https://codeforces.com/problemset/submit")

    form = page.locator("input[name=submittedProblemCode]")
    enter = page.locator("a[href^='/enter']")
    form.or_(enter).first.wait_for(timeout=60_000)

    if form.count() == 0:
        print("Not logged in. Run: cfx login")
        ctx.close(); p.stop(); return

    page.fill("input[name=submittedProblemCode]", problem)
    page.select_option("select[name=programTypeId]", lang)
    page.set_input_files("input[name=sourceFile]", str(src))
    page.click("#singlePageSubmitButton")
    page.wait_for_load_state()
    watch(ctx, get_handle(page), get_sub_id(page))
    ctx.close(); p.stop()
def cmd_login(args):
    login()

def cmd_emit(args):
    emit(args.problem, args.file)

def cmd_fetch(args):
    contest, index = split_code(args.problem)
    soup = get_page(contest, index)
    folder = Path(contest + index)
    n = save_samples(soup, folder)
    parts = statement_parts(soup)
    (folder / "statement.md").write_text(statement_md(parts))
    show_statement(parts)
    console.print(f"\n[dim]Saved statement and {n} sample(s) to {folder}/[/]")


def cmd_add(args):
    contest, index = split_code(args.problem)
    add_test(Path(contest + index))
def find_source(problem, name):
    for path in (Path(name), Path(problem.upper()) / Path(name).name):
        if path.exists():
            if path.suffix not in LANGS:
                raise SystemExit(f"Can't handle {path.suffix} files yet. "
                                 f"Supported: {', '.join(LANGS)}")
            return path
    raise SystemExit(f"File not found: {name} (looked here and in {problem.upper()}/)")
def cmd_test(args):
    contest, index = split_code(args.problem)
    run_tests(Path(contest+index), find_source(args.problem, args.file))

    folder = Path(contest + index)
    src = Path(args.file)
    if not src.exists():
        src = folder / args.file
    run_tests(folder, src)
def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description="Codeforces from your terminal: fetch, test, submit.",
        epilog=EXAMPLES,
        formatter_class=Fmt,
    )

    parser.add_argument("-V", "--version", action="version",
                        version=f"atharva {version('atharva')}")
    sub = parser.add_subparsers(dest="cmd", title="commands", metavar="<command>")

    def command(name, func, help, problem=False, file=False):
        p = sub.add_parser(name, help=help, description=help, formatter_class=Fmt)
        if problem:
            p.add_argument("problem", help="problem code, e.g. 1878E or 71A")
        if file:
            p.add_argument("file", help="your solution, e.g. ans.cpp or ans.py")
        p.set_defaults(func=func)

    command("login", cmd_login, "log in to Codeforces (one time)")
    command("fetch", cmd_fetch, "get the statement and sample tests", problem=True)
    command("add",   cmd_add,   "add a custom test by pasting it", problem=True)
    command("test",  cmd_test,  "run your solution against all tests", problem=True, file=True)
    command("emit",  cmd_emit,  "submit and watch the live verdict", problem=True, file=True)

    args = parser.parse_args()
    if args.cmd is None:
        parser.print_help()
    else:
        try:
            args.func(args)
        except KeyboardInterrupt:
            raise SystemExit("\nCancelled.", flush=True)
        os._exit(130)
    
    