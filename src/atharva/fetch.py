import re
from pathlib import Path
from bs4 import BeautifulSoup
from .browser import open_cf

# ---------- fetching ----------

def split_code(code):
    m = re.fullmatch(r"(\d+)([A-Za-z]\d*)", code)
    if not m:
        raise SystemExit(f"Bad problem code: {code}")
    return m.group(1), m.group(2).upper()

def get_page(contest, index):
    p, ctx = open_cf()
    url = f"https://codeforces.com/problemset/problem/{contest}/{index}"
    html = ctx.request.get(url).text()

    if "problem-statement" not in html:
        page = ctx.new_page()
        page.goto(url)
        page.wait_for_selector("div.problem-statement", timeout=60_000)
        html = ctx.request.get(url).text()

    ctx.close(); p.stop()
    if "problem-statement" not in html:
        raise SystemExit(f"Couldn't load problem {contest}{index}. Check the code, or run: cfx login")
    return BeautifulSoup(html, "html.parser")

# ---------- samples ----------

def pre_text(pre):
    lines = pre.select("div.test-example-line")
    if lines:
        return "\n".join(d.get_text() for d in lines).strip() + "\n"
    for br in pre.find_all("br"):
        br.replace_with("\n")
    return pre.get_text().strip() + "\n"

def save_samples(soup, folder):
    tests = folder / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    for old in tests.glob("s*.*"):
        old.unlink()
    ins = soup.select("div.sample-test div.input pre")
    outs = soup.select("div.sample-test div.output pre")
    for i, (a, b) in enumerate(zip(ins, outs), start=1):
        (tests / f"s{i}.in").write_text(pre_text(a))
        (tests / f"s{i}.out").write_text(pre_text(b))
    return len(ins)

# ---------- math ----------

SYMBOLS = {
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠",
    "lt": "<", "gt": ">", "cdot": "·", "times": "×", "ldots": "…",
    "dots": "…", "cdots": "…", "oplus": "⊕", "land": "&", "lor": "|",
    "lfloor": "⌊", "rfloor": "⌋", "lceil": "⌈", "rceil": "⌉",
    "sum": "Σ", "infty": "∞", "in": "∈", "to": "→", "mid": "|",
    "min": "min", "max": "max", "gcd": "gcd", "bmod": "mod", "mod": "mod",
}

SUB_FROM = "0123456789+-=()aehijklmnoprstuvx"
SUB_TO   = "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"
SUP_FROM = "0123456789+-=()ni"
SUP_TO   = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ"
SUB = str.maketrans(SUB_FROM, SUB_TO)
SUP = str.maketrans(SUP_FROM, SUP_TO)

def script(mark, body):
    body = body.replace(" ", "")
    allowed, table = (SUB_FROM, SUB) if mark == "_" else (SUP_FROM, SUP)
    if body and all(c in allowed for c in body):
        return body.translate(table)
    return f"{mark}({body})" if len(body) > 1 else mark + body

def convert(s):
    s = s.replace(r"\{", "⟨LB⟩").replace(r"\}", "⟨RB⟩")
    s = re.sub(r"\\(?:operatorname|texttt|text|mathrm|textbf|mathit)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\([A-Za-z]+)", lambda m: SYMBOLS.get(m.group(1), m.group(1)), s)
    s = re.sub(r"\\(.)", r"\1", s)
    s = re.sub(r"([_^])\{([^{}]*)\}", lambda m: script(m.group(1), m.group(2)), s)
    s = re.sub(r"([_^])([A-Za-z0-9])", lambda m: script(m.group(1), m.group(2)), s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("⟨LB⟩", "{").replace("⟨RB⟩", "}")
    return re.sub(r"\s+", " ", s).strip()

def math(m):
    return "`" + convert(m.group(1)) + "`"

def tex(s):
    s = re.sub(r"\$\$\$\$\$\$(.+?)\$\$\$\$\$\$", math, s, flags=re.S)
    s = re.sub(r"\$\$\$(.+?)\$\$\$", math, s, flags=re.S)
    return re.sub(r" {2,}", " ", s)

# ---------- statement ----------

def section(el):
    parts = []
    for node in el.find_all(["p", "li"]):
        prefix = "- " if node.name == "li" else ""
        parts.append(prefix + tex(node.get_text()))
    return "\n\n".join(parts)

def statement_parts(soup):
    st = soup.select_one("div.problem-statement")
    hdr = st.select_one("div.header")

    def prop(cls):
        el = hdr.select_one(f"div.{cls}")
        el.select_one("div.property-title").extract()
        return el.get_text(strip=True)

    ins = soup.select("div.sample-test div.input pre")
    outs = soup.select("div.sample-test div.output pre")
    note = st.select_one("div.note")
    return {
        "title": hdr.select_one("div.title").get_text(strip=True),
        "time": prop("time-limit"),
        "memory": prop("memory-limit"),
        "legend": section(st.find_all("div", recursive=False)[1]),
        "input": section(st.select_one("div.input-specification")),
        "output": section(st.select_one("div.output-specification")),
        "samples": [(pre_text(a), pre_text(b)) for a, b in zip(ins, outs)],
        "note": section(note) if note else "",
    }

def statement_md(s):
    md = [
        f"# {s['title']}",
        f"*time: {s['time']} · memory: {s['memory']}*",
        s["legend"],
        "## Input", s["input"],
        "## Output", s["output"],
    ]
    for i, (a, b) in enumerate(s["samples"], start=1):
        md += [f"## Sample {i}", "**Input**", f"```\n{a}```", "**Output**", f"```\n{b}```"]
    if s["note"]:
        md += ["## Note", s["note"]]
    return "\n\n".join(md)
