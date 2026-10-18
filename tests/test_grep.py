import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from test_cases import FIXTURE, TestCase, cases

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


class TestsTrackerObject:
    def __init__(self, total: int):
        self.passed = 0
        self.failed = 0
        self.total = total
        self.start: float | None = None


tracker = TestsTrackerObject(total=len(cases))


class FailedTest(Exception):
    def __init__(self, failure_info: str):
        super().__init__()

        self.failure_info = failure_info


def test_pattern_on_corpus(grep_exe: Path, corpus_path: Path, case: TestCase) -> None:
    """Runs one case against its corpus and raises FailedTest if it
    does not return the expected output"""

    res = subprocess.run(
        [grep_exe.absolute(), *case.flags, corpus_path.absolute(), case.pattern],
        capture_output=True,
        check=False,
    )

    grep_out = res.stdout.decode().splitlines()
    expected_lines = case.expected_lines

    if case.any_order:
        grep_out, expected_lines = sorted(grep_out), sorted(expected_lines)
    lines_correct = grep_out == expected_lines
    stderr_empty = res.stderr == b""

    if lines_correct and stderr_empty:
        return

    else:
        info = f"pattern: {label(case)}\n"

        if not stderr_empty:
            info += f"stderr:\n{res.stderr.decode()}"

        if not lines_correct:
            info += f"expected lines:\n{expected_lines}\n\ngot lines:\n{grep_out}"

        raise FailedTest(failure_info=info)


def label(case: TestCase) -> str:
    return " ".join([*case.flags, case.pattern])


def write_fixture(root: Path) -> None:
    for name, content in FIXTURE.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def update_quiet():
    text = f"{tracker.passed} Passed, {tracker.failed} Failed, In {time.time() - tracker.start:.2f}s"
    if tracker.failed > 0:
        print("\r", RED, text, RESET, end="")
    else:
        print("\r", GREEN, text, RESET, end="")


def main():
    parser = argparse.ArgumentParser(description="Tests for the grep script in ../")

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Clean up the output"
    )

    args = parser.parse_args()

    grep_exe = Path(__file__).parent.parent / "build" / "Release" / "grep.exe"
    corpus_folder = Path(__file__).parent / "test-corpus-old-grep"
    fixture = tempfile.TemporaryDirectory()
    write_fixture(Path(fixture.name))

    tracker.start = time.time()

    for case in cases:
        try:
            test_pattern_on_corpus(
                grep_exe=grep_exe,
                corpus_path=Path(fixture.name) / case.corpus
                if case.corpus
                else corpus_folder,
                case=case,
            )
            tracker.passed += 1

            if args.quiet:
                update_quiet()
            else:
                print(GREEN, label(case), RESET)

        except FailedTest as e:
            tracker.failed += 1

            if args.quiet:
                update_quiet()
            else:
                print(RED, e.failure_info, RESET)

    if tracker.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
