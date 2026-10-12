import sys

def next_number(tests):
    n = 1
    while (tests / f"c{n}.in").exists():
        n += 1
    return n

def add_test(folder):
    tests = folder / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    n = next_number(tests)

    print("Paste input, then press Ctrl+D on a new line:")
    inp = sys.stdin.read()
    if not inp.strip():
        print("Empty input, nothing saved.")
        return
    (tests / f"c{n}.in").write_text(inp.rstrip("\n") + "\n")

    print("Paste expected output, then Ctrl+D (or just Ctrl+D to skip):")
    out = sys.stdin.read()
    if out.strip():
        (tests / f"c{n}.out").write_text(out.rstrip("\n") + "\n")
        print(f"Saved c{n} (input + expected output)")
    else:
        print(f"Saved c{n} (input only, test will just show your output)")