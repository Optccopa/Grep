"""Benchmark this grep against ripgrep and GNU grep. Usage: python bench.py [--fast]"""

import os
import statistics
import subprocess
import sys
import time

MINE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "build", "Release", "grep.exe"
)
RG = "rg"
# prefer MSYS2's native GNU grep, fall back to the older one bundled with Git
GNU = next(
    (
        p
        for p in (
            r"C:\msys64\ucrt64\bin\grep.exe",
            r"C:\Program Files\Git\usr\bin\grep.exe",
        )
        if os.path.isfile(p)
    ),
    None,
)
SMALL = r"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\MSVC\14.51.36231\include"
LARGE = r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0"

# [(] not \( since some grep builds mangle backslashes in args
CASES = [
    ("Small", SMALL, "literal", "constexpr"),
    ("Small", SMALL, "regex", "_[A-Z]+_[A-Z]+[(]"),
    ("Small", SMALL, "no match", "zqxjvk"),
    ("Large", LARGE, "literal", "HRESULT"),
    ("Large", LARGE, "regex", "_[A-Z]+_[A-Z]+[(]"),
    ("Large", LARGE, "no match", "zqxjvk"),
]

RUNS = 1 if "--fast" in sys.argv else 20

for d in (SMALL, LARGE):
    if not os.path.isdir(d):
        sys.exit(f"Directory not found: {d}")
if not GNU:
    sys.exit("GNU grep not found (install MSYS2 or Git for Windows)")
print(
    subprocess.run(
        [GNU, "--version"], capture_output=True, text=True, check=False
    ).stdout.splitlines()[0]
)


# same output for all: matching lines only, no filename/line number, skip binary
def cmds(path, pat):
    return {
        "this grep": [MINE, path, pat],
        "ripgrep": [RG, "-IN", "--no-heading", pat, path],
        "GNU grep": [GNU, "-rhIE", pat, path],
    }


def timed(cmd):
    t = time.perf_counter()
    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
    )
    return (time.perf_counter() - t) * 1000


rows = []
for size, path, kind, pat in CASES:
    res = {}
    for name, cmd in cmds(path, pat).items():
        # exit code 1 = no match, so no check; this run also warms the file cache
        lines = subprocess.run(cmd, capture_output=True, check=False).stdout.count(
            b"\n"
        )
        res[name] = statistics.median(timed(cmd) for _ in range(RUNS))
        print(f"{size} {kind} {name}: {res[name]:.0f} ms, {lines} lines", flush=True)
    rows.append((size, kind, pat, res))

names = ["this grep", "ripgrep", "GNU grep"]
print("\n| Corpus | Search | " + " | ".join(names) + " |")
print("|---|---|" + "---:|" * len(names))
for size, kind, pat, res in rows:
    best = min(res.values())
    cells = [
        f"**{res[n]:.0f} ms**" if res[n] == best else f"{res[n]:.0f} ms" for n in names
    ]
    print(f"| {size} | {kind} `{pat}` | " + " | ".join(cells) + " |")
