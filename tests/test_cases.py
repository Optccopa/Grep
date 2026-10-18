class TestCase:
    def __init__(self, pattern: str, expected_lines: list[str]):
        self.pattern = pattern
        self.expected_lines = expected_lines


# Extend tests here
cases: list[TestCase] = [
    TestCase(
        r"{{config}}",
        [
            "    cmake --build build --config {{config}}",
            "    cmake --build build --config {{config}}",
            '    powershell -Command "./build/{{config}}/grep.exe . conf"',
        ],
    ),
    TestCase(
        r"^cmake_minimum_required\(.*\)$", ["cmake_minimum_required(VERSION 3.28)"]
    ),
    TestCase(r"[0-9]+\.[0-9]+\)$", ["cmake_minimum_required(VERSION 3.28)"]),
    TestCase(
        r"^#include <(vector|string)>$", ["#include <string>", "#include <vector>"]
    ),
    TestCase(
        r'grep\.exe .* conf"$',
        ['    powershell -Command "./build/{{config}}/grep.exe . conf"'],
    ),
    TestCase(
        "int main",
        ["int main(int argc, char* argv[]) {"],
    ),
    TestCase(
        "\\bvoid\\b",
        [
            "void grepFile(const std::filesystem::path& path, const pcre2_code* expression,"
        ],
    ),
    TestCase(
        "return [0-9]+;",
        ["        return 2;", "        return 0;", "    return 0;"],
    ),
    TestCase(
        "^\\s*//",
        ["    // also folders starting in ."],
    ),
    TestCase(
        "for \\(",
        [
            "        for (size_t read = 0; read < got; ++read) {",
            "    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);",
            "    for (unsigned t = 0; t < threadCount; ++t) {",
            "            for (;;) {",
            "    for (auto& thread : threads) {",
        ],
    ),
    TestCase(
        "\\.size\\(\\)",
        [
            "        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));",
            "                if (i >= files.size()) { break; }",
        ],
    ),
    TestCase(
        "std::vector<[a-z:]+>",
        [
            "std::vector<std::filesystem::path> collectFiles(const std::filesystem::path& dir) {",
            "    std::vector<std::filesystem::path> files;",
            "    const std::vector<std::filesystem::path> files = collectFiles(dir);",
            "    std::vector<std::thread> threads;",
        ],
    ),
    TestCase(
        "VERSION",
        ["cmake_minimum_required(VERSION 3.28)"],
    ),
    TestCase(
        "powershell",
        [
            "    powershell -Command \"if (Test-Path 'build') { Remove-Item -Path 'build' -Recurse -Force }\"",
            '    powershell -Command "./build/{{config}}/grep.exe . conf"',
        ],
    ),
    TestCase(
        "^\\s+@clear$",
        ["    @clear", "    @clear", "    @clear"],
    ),
    TestCase(
        "^configure:$",
        ["configure:"],
    ),
    TestCase(
        "^run ",
        ['run config="Release":'],
    ),
    TestCase(
        "Force \\}",
        [
            "    powershell -Command \"if (Test-Path 'build') { Remove-Item -Path 'build' -Recurse -Force }\""
        ],
    ),
    TestCase(
        "python",
        [
            '"""Benchmark this grep against ripgrep and GNU grep. Usage: python bench.py [--fast]"""'
        ],
    ),
    TestCase(
        "^import ",
        [
            "import os",
            "import statistics",
            "import subprocess",
            "import sys",
            "import time",
        ],
    ),
    TestCase(
        "^import (os|sys|time)",
        ["import os", "import sys", "import time"],
    ),
    TestCase(
        "def [a-z_]+\\(",
        ["def cmds(path, pat):", "def timed(cmd):"],
    ),
    TestCase(
        "__file__",
        [
            '    os.path.dirname(os.path.abspath(__file__)), "build", "Release", "grep.exe"'
        ],
    ),
    TestCase(
        "subprocess",
        [
            "import subprocess",
            'print(subprocess.run([GNU, "--version"], capture_output=True, text=True, check=False).stdout.splitlines()[0])',
            "    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)",
            '        lines = subprocess.run(cmd, capture_output=True, check=False).stdout.count(b"\\n")',
        ],
    ),
    TestCase(
        "median",
        ["        res[name] = statistics.median(timed(cmd) for _ in range(RUNS))"],
    ),
    TestCase(
        "statistics",
        [
            "import statistics",
            "        res[name] = statistics.median(timed(cmd) for _ in range(RUNS))",
        ],
    ),
    TestCase(
        "\\| Small",
        [
            "| Small | literal `constexpr` | **16 ms** | 23 ms | 110 ms |",
            "| Small | regex `_[A-Z]+_[A-Z]+[(]` | **18 ms** | 25 ms | 158 ms |",
            "| Small | no match `zqxjvk` | **16 ms** | 23 ms | 111 ms |",
        ],
    ),
    TestCase(
        "\\| Large",
        [
            "| Large | literal `HRESULT` | 183 ms | **123 ms** | 1587 ms |",
            "| Large | regex `_[A-Z]+_[A-Z]+[(]` | 172 ms | **138 ms** | 2101 ms |",
            "| Large | no match `zqxjvk` | 167 ms | **118 ms** | 1782 ms |",
        ],
    ),
    TestCase(
        "[0-9]+ ms",
        [
            "| Small | literal `constexpr` | **16 ms** | 23 ms | 110 ms |",
            "| Small | regex `_[A-Z]+_[A-Z]+[(]` | **18 ms** | 25 ms | 158 ms |",
            "| Small | no match `zqxjvk` | **16 ms** | 23 ms | 111 ms |",
            "| Large | literal `HRESULT` | 183 ms | **123 ms** | 1587 ms |",
            "| Large | regex `_[A-Z]+_[A-Z]+[(]` | 172 ms | **138 ms** | 2101 ms |",
            "| Large | no match `zqxjvk` | 167 ms | **118 ms** | 1782 ms |",
        ],
    ),
    TestCase(
        "```",
        ["```bash", "```"],
    ),
    TestCase(
        "C\\+\\+20",
        [
            "A simple grep tool written in C++20, ~3x faster than GNU grep and matches ripgrep on small folders."
        ],
    ),
    TestCase(
        "git clone",
        ["git clone https://github.com/Optccopa/Grep"],
    ),
    TestCase(
        "Optccopa",
        ["git clone https://github.com/Optccopa/Grep"],
    ),
    TestCase(
        "Ryzen",
        ["## Benchmarks (Windows 11, Ryzen 7 5700G (8C/16T))"],
    ),
    TestCase(
        "^\\|---",
        ["|---|---|---:|---:|---:|"],
    ),
    TestCase(
        "[0-9]+(\\.[0-9]+)? MB",
        [
            "- **Small:** MSVC STL headers, 353 files, 15 MB",
            "- **Large:** Windows SDK 10.0.26100.0 headers, 4,771 files, 345 MB",
        ],
    ),
    TestCase(
        "^- \\*\\*",
        [
            "- **Small:** MSVC STL headers, 353 files, 15 MB",
            "- **Large:** Windows SDK 10.0.26100.0 headers, 4,771 files, 345 MB",
        ],
    ),
    TestCase(
        "main\\(",
        ["int main(int argc, char* argv[]) {"],
    ),
    TestCase(
        "argc",
        ["int main(int argc, char* argv[]) {", "    if (argc < 3) {"],
    ),
    TestCase(
        "atomic",
        ["#include <atomic>", "    std::atomic<size_t> nextFile{0};"],
    ),
    TestCase(
        "\\bint\\b",
        [
            "    int errcode;",
            "        int rc = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(buf.data()),",
            "int main(int argc, char* argv[]) {",
        ],
    ),
    TestCase(
        "\\bTrue\\b",
        [
            'print(subprocess.run([GNU, "--version"], capture_output=True, text=True, check=False).stdout.splitlines()[0])',
            '        lines = subprocess.run(cmd, capture_output=True, check=False).stdout.count(b"\\n")',
            '        print(f"{size} {kind} {name}: {res[name]:.0f} ms, {lines} lines", flush=True)',
        ],
    ),
    TestCase(
        "print\\(",
        [
            'print(subprocess.run([GNU, "--version"], capture_output=True, text=True, check=False).stdout.splitlines()[0])',
            '        print(f"{size} {kind} {name}: {res[name]:.0f} ms, {lines} lines", flush=True)',
            'print("\\n| Corpus | Search | " + " | ".join(names) + " |")',
            'print("|---|---|" + "---:|" * len(names))',
            '    print(f"| {size} | {kind} `{pat}` | " + " | ".join(cells) + " |")',
        ],
    ),
    TestCase(
        "\\$<",
        ['set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")'],
    ),
    TestCase(
        "<string>\\n#include <vector>",
        [],
    ),
    TestCase(
        "<string>\\s#include",
        [],
    ),
    TestCase(
        "(?s)<string>.#include <vector>",
        [],
    ),
    TestCase(
        "\\{\\n    int errcode",
        [],
    ),
    TestCase(
        "\\S\\n\\S",
        [],
    ),
    TestCase(
        ";\\n",
        [],
    ),
    TestCase(
        "\\n",
        [],
    ),
    TestCase(
        "return 0;\\n\\}",
        [],
    ),
    TestCase(
        "(?s)^configure:.*?@clear",
        [],
    ),
    TestCase(
        "configure:\\s+@clear",
        [],
    ),
    TestCase(
        "\\W{2,}$\\n",
        [],
    ),
    TestCase(
        "^$",
        [""] * 72,
    ),
    TestCase(
        "^\\s*$",
        [""] * 72,
    ),
    TestCase(
        "(?=VERSION)",
        ["cmake_minimum_required(VERSION 3.28)"],
    ),
    TestCase(
        "VERSION(?! 4)",
        ["cmake_minimum_required(VERSION 3.28)"],
    ),
    TestCase(
        "VERSION(?! 3)",
        [],
    ),
    TestCase(
        "@clear\\r",
        [],
    ),
    TestCase(
        "\\r",
        [],
    ),
    TestCase(
        "\\r$",
        [],
    ),
    TestCase(
        "clear$",
        ["    @clear", "    @clear", "    @clear"],
    ),
    TestCase(
        "runs-on",
        [],
    ),
    TestCase(
        "\\[core\\]",
        [],
    ),
    TestCase(
        "ignorecase",
        [],
    ),
    TestCase(
        "^(x+x+)+y",
        [],
    ),
    TestCase(
        "(a|aa)+$",
        [],
    ),
    TestCase(
        "(?>a+)a",
        [],
    ),
    TestCase(
        "a++a",
        [],
    ),
    TestCase(
        "^(\\w)\\w*\\1$",
        [],
    ),
    TestCase(
        "\\x00",
        [],
    ),
    TestCase(
        "^#define PCRE2",
        ["#define PCRE2_CODE_UNIT_WIDTH 8"],
    ),
    TestCase(
        "^#include <pcre2.h>",
        ["#include <pcre2.h>"],
    ),
    TestCase(
        "^import os",
        ["import os"],
    ),
    TestCase(
        "(?<=SOFTWARE\\.\\n)\\z",
        [],
    ),
    TestCase(
        "(?<=SOFTWARE\\.\\n)$",
        [],
    ),
    TestCase(
        "\\{\\{[^}]*\\}\\}",
        [
            "    cmake --build build --config {{config}}",
            "    cmake --build build --config {{config}}",
            '    powershell -Command "./build/{{config}}/grep.exe . conf"',
        ],
    ),
    TestCase(
        "\\x20{4}\\x40",
        ["    @clear", "    @clear", "    @clear"],
    ),
    TestCase(
        "\\\\\\\\",
        [],
    ),
    TestCase(
        "(?<=\n)$",
        [""] * 72,
    ),
]
