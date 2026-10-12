import re, shutil, subprocess, sys, time
from pathlib import Path
from .langs import LANGS
from . import report

def need(tool):
    if not shutil.which(tool):
        raise SystemExit(f"'{tool}' not found. Install it to run {tool} files.")

def build(src):
    lang = LANGS.get(src.suffix)
    if lang is None:
        raise SystemExit(f"Can't run {src.suffix} files yet")

    if "run" in lang:
        need(lang["run"][0])
        return [*lang["run"], str(src)]

    exe = src.with_suffix("")
    if not exe.exists() or exe.stat().st_mtime < src.stat().st_mtime:
        need(lang["compile"][0])
        cmd = [*lang["compile"], str(src), "-o", str(exe), *lang.get("libs", [])]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr)
            return None
    return [str(exe.resolve())]

def run_one(cmd, inp, tl):
    start = time.perf_counter()
    try:
        r = subprocess.run(cmd, input=inp, capture_output=True, text=True, timeout=tl)
    except subprocess.TimeoutExpired:
        return "TLE", "", "", tl
    t = time.perf_counter() - start
    status = "RE" if r.returncode != 0 else "RAN"
    return status, r.stdout, r.stderr, t

def time_limit(folder):
    md = folder / "statement.md"
    if md.exists():
        m = re.search(r"time: ([\d.]+) second", md.read_text())
        if m:
            return float(m.group(1))
    return 2.0

def test_order(path):
    return (path.stem[0], int(path.stem[1:]))

def run_tests(folder, src):
    cmd = build(src)
    if cmd is None:
        return
    tl = time_limit(folder)

    tests = sorted((folder / "tests").glob("*.in"), key=test_order)
    if not tests:
        raise SystemExit(f"No tests for {folder.name}. Run: cfx fetch {folder.name}")
    passed = 0
    for inp in tests:
        exp = inp.with_suffix(".out")
        status, out, err, t = run_one(cmd, inp.read_text(), tl)
        if status == "RAN":
            if not exp.exists():
                status = "NO ANSWER"
            elif out.split() == exp.read_text().split():
                status = "OK"
            else:
                status = "WA"

        report.badge(inp.stem, status, t)
        if status == "OK":
            passed += 1
        elif status == "WA":
            report.diff(out, exp.read_text())
        elif status == "NO ANSWER":
            report.console.print(out.rstrip())
        report.stderr_box(err)

    report.summary(passed, len(tests))
