import argparse
import subprocess
import sys
import time
from pathlib import Path

from test_cases import cases

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


def test_pattern_on_corpus(
    grep_exe: Path, corpus_path: Path, pattern: str, expected_lines: list
) -> None:

    res = subprocess.run(
        [grep_exe.absolute(), corpus_path.absolute(), pattern],
        capture_output=True,
        check=False,
    )

    grep_out = res.stdout.decode().splitlines()

    lines_correct = grep_out == expected_lines
    stderr_empty = res.stderr == b""

    if lines_correct and stderr_empty:
        return

    else:
        info = f"pattern: {pattern}\n"

        if not stderr_empty:
            info += f"stderr:\n{res.stderr.decode()}"

        if not lines_correct:
            info += f"expected lines:\n{expected_lines}\n\ngot lines:\n{grep_out}"

        raise FailedTest(failure_info=info)


def update_quiet():
    text = f"Passed: {tracker.passed}, Failed: {tracker.failed}, In {time.time() - tracker.start:.2f}s"
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

    tracker.start = time.time()

    for case in cases:
        try:
            test_pattern_on_corpus(
                grep_exe=grep_exe,
                corpus_path=corpus_folder,
                pattern=case.pattern,
                expected_lines=case.expected_lines,
            )
            tracker.passed += 1

            if args.quiet:
                update_quiet()
            else:
                print(GREEN, case.pattern, RESET)

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
