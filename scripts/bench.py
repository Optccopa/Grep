"""Benchmark this grep against ripgrep and GNU grep. Usage: python bench.py [--fast]

Every table cell is the mean, over all FLAG_SETS, of the median time of that search run with those flags.
"""

import os
import statistics
import subprocess
import sys
import time

MINE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "build", "Release", "grep.exe"
)
RG = "rg"
GNU = r"C:\Program Files\Git\usr\bin\grep.exe"
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

# averaged into every cell
FLAG_SETS = [
    [],
    ["-i"],
    ["-S"],
    ["-F"],
    ["-w"],
    ["-x"],
    ["-v"],
    ["-i", "-w"],
    ["-i", "-F"],
    ["-i", "-v"],
]

RUNS = 1 if "--fast" in sys.argv else 10

for d in (SMALL, LARGE):
    if not os.path.isdir(d):
        sys.exit(f"Directory not found: {d}")
if not os.path.isfile(GNU):
    sys.exit("GNU grep not found (install Git for Windows)")
GNU_NAME = (
    "GNU grep "
    + subprocess.run(
        [GNU, "--version"], capture_output=True, text=True, check=False
    ).stdout.split()[3]
)
NAMES = ["this grep", "ripgrep", GNU_NAME]


def has_uppercase(pattern):
    """Same rule as this grep's -S: the letter after a backslash is an escape, not a literal."""
    i = 0
    while i < len(pattern):
        if pattern[i] == "\\":
            i += 2
            continue
        if pattern[i].isupper():
            return True
        i += 1
    return False


def gnu_flags(flags, pat):
    # GNU grep has no smart case, so -S becomes -i when the pattern has no uppercase letter
    # and -F replaces -E, since grep 3.0 rejects both together
    out = ["-rhI", "-F" if "-F" in flags else "-E"]
    out += [f for f in flags if f not in ("-F", "-S")]
    if "-S" in flags and not has_uppercase(pat) and "-i" not in out:
        out.append("-i")
    return out


# same output for all: matching lines only, no filename/line number, skip binary
def cmds(path, pat, flags):
    # --crlf lets ripgrep's -x see CRLF line ends the way this grep does
    crlf = ["--crlf"] if "-x" in flags else []
    return {
        "this grep": [MINE, *flags, path, pat],
        "ripgrep": [RG, "-IN", "--no-heading", *crlf, *flags, pat, path],
        GNU_NAME: [GNU, *gnu_flags(flags, pat), pat, path],
    }


def timed(cmd):
    t = time.perf_counter()
    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
    )
    return (time.perf_counter() - t) * 1000


rows = []
mismatches = []
for size, path, kind, pat in CASES:
    medians = {name: [] for name in NAMES}
    mismatched = False
    for flags in FLAG_SETS:
        commands = cmds(path, pat, flags)
        # exit code 1 = no match, so no check; this run also warms the file cache
        lines = {
            name: subprocess.run(cmd, capture_output=True, check=False).stdout.count(
                b"\n"
            )
            for name, cmd in commands.items()
        }
        times = {name: [] for name in NAMES}
        for _ in range(RUNS):
            # interleaved, so drift during the run hits every tool equally
            for name, cmd in commands.items():
                times[name].append(timed(cmd))
        flag_text = " ".join(flags) or "(none)"
        for name in NAMES:
            medians[name].append(statistics.median(times[name]))
        if len(set(lines.values())) > 1:
            mismatched = True
            mismatches.append(
                f"{size} {kind} `{pat}` {flag_text}: "
                + ", ".join(f"{n} {lines[n]}" for n in NAMES)
            )
        print(
            f"{size} {kind} {flag_text:8} "
            + "  ".join(
                f"{n}: {medians[n][-1]:.0f} ms, {lines[n]} lines" for n in NAMES
            ),
            flush=True,
        )
    rows.append(
        (
            size,
            kind,
            pat,
            {n: statistics.mean(v) for n, v in medians.items()},
            mismatched,
        )
    )

print(
    f"\nEach cell: mean over {len(FLAG_SETS)} flag sets of the median of {RUNS} runs. Flag sets: "
    + ", ".join(" ".join(f) or "(none)" for f in FLAG_SETS)
)
print("\n| Corpus | Search | " + " | ".join(NAMES) + " |")
print("|---|---|" + "---:|" * len(NAMES))
for size, kind, pat, res, mismatched in rows:
    best = min(res.values())
    cells = [
        f"**{res[n]:.0f} ms**" if res[n] == best else f"{res[n]:.0f} ms" for n in NAMES
    ]
    mark = " †" if mismatched else ""
    print(f"| {size} | {kind} `{pat}`{mark} | " + " | ".join(cells) + " |")

if mismatches:
    print(
        "\n† line counts differ between tools for these flag sets, so the work is not identical:"
    )
    for m in mismatches:
        print(f"  {m}")
