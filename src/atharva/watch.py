
import time
from rich.text import Text
from .report import console

NAMES = {
    "OK": "Accepted",
    "WRONG_ANSWER": "Wrong answer",
    "TIME_LIMIT_EXCEEDED": "Time limit exceeded",
    "MEMORY_LIMIT_EXCEEDED": "Memory limit exceeded",
    "RUNTIME_ERROR": "Runtime error",
    "COMPILATION_ERROR": "Compilation error",
    "IDLENESS_LIMIT_EXCEEDED": "Idleness limit exceeded",
}
STYLES = {
    "OK": "green", "WRONG_ANSWER": "red",
    "TIME_LIMIT_EXCEEDED": "yellow", "MEMORY_LIMIT_EXCEEDED": "yellow",
    "RUNTIME_ERROR": "magenta", "COMPILATION_ERROR": "blue",
}

def watch(ctx, handle, sub_id):
    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=5"
    with console.status("In queue...", spinner="dots") as status:
        while True:
            data = ctx.request.get(url).json()
            if data.get("status") == "OK":
                sub = next((s for s in data["result"] if s["id"] == sub_id), None)
                if sub:
                    v = sub.get("verdict", "QUEUED")
                    if v not in ("TESTING", "QUEUED"):
                        break
                    if v == "TESTING":
                        status.update(f"Running on test {sub['passedTestCount'] + 1}...")
            time.sleep(2)
    show_verdict(sub)
    return sub

def show_verdict(sub):
    v = sub["verdict"]
    name = NAMES.get(v, v.replace("_", " ").capitalize())
    if v not in ("OK", "COMPILATION_ERROR"):
        name += f" on test {sub['passedTestCount'] + 1}"
    style = STYLES.get(v, "white")
    stats = f"{sub['timeConsumedMillis']} ms · {sub['memoryConsumedBytes'] // 1024} KB"
    console.print(Text.assemble((f" {name} ", f"bold reverse {style}"), "  ", (stats, "dim")))
    link = f"https://codeforces.com/problemset/submission/{sub['contestId']}/{sub['id']}"
    console.print(Text(link, style=f"dim link {link}"))

def get_handle(page):
    link = page.locator("#header a[href^='/profile/']").first
    return link.inner_text().strip()

def get_sub_id(page):
    row = page.locator("tr[data-submission-id]").first
    return int(row.get_attribute("data-submission-id"))

