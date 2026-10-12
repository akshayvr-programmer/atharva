import shutil, sys

LANGS = {
    ".cpp":  {"id": "91", "compile": ["g++", "-std=c++20", "-O2", "-Wall", "-DLOCAL"]},
    ".c":    {"id": "43", "compile": ["gcc", "-std=c11", "-O2", "-Wall", "-DLOCAL"], "libs": ["-lm"]},
    ".rs":   {"id": "98", "compile": ["rustc", "-O", "--edition=2024"]},
    ".py":   {"id": "70", "run": [shutil.which("pypy3") or sys.executable]},
    ".java": {"id": "87", "run": ["java"]},
}

OVERRIDES = {
    "py3":   "31",
    "g++20": "89",
}
