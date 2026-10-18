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
        '=\\s*\\w+;',
        ['        size_t write = 0;', '        for (size_t read = 0; read < got; ++read) {', '        got = write;', '    size_t pos = 0;', '        bool matched = true;', '                                  lineEnd - lineStart, 0, 0, matchData.get(), nullptr) >= 0;', '    if (threadCount == 0) { threadCount = 4; }', '    for (unsigned t = 0; t < threadCount; ++t) {'],
    ),
    TestCase(
        '(?:st|ri){2}',
        ['#include <string>', '#include <cstring>', '#include <string_view>', 'constexpr std::array<std::string_view, 6> ignoredFolders{', '        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));', '              std::string& buf, std::string& out) {', '        std::cerr << path.string() << ": Failed to open\\n";', '        if (rc < 0) { throw std::runtime_error("Match error: " + std::to_string(rc)); }', "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", '        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;', '            const std::string fileName = entry.path().filename().string();', '        std::string buf, out;', '            std::string buf, out;', '                    std::cerr << files[i].string() << ": " << e.what() << "\\n";'],
    ),
    TestCase(
        '(\\w+::){2,}',
        ['void grepFile(const std::filesystem::path& path, const pcre2_code* expression,', '    std::ifstream file(path, std::ios::binary);', '    file.seekg(0, std::ios::end);', '    file.seekg(0, std::ios::beg);', "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", '        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;', 'std::vector<std::filesystem::path> collectFiles(const std::filesystem::path& dir) {', '    std::vector<std::filesystem::path> files;', '    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);', '        it != std::filesystem::recursive_directory_iterator(); ++it) {', '            if (fileName.starts_with(".") || std::ranges::find(ignoredFolders, fileName) != ignoredFolders.end()) {', '    std::filesystem::path dir = std::filesystem::current_path();', '    if (std::filesystem::is_regular_file(dir)) {', '    const std::vector<std::filesystem::path> files = collectFiles(dir);', '    unsigned threadCount = std::thread::hardware_concurrency();'],
    ),
    TestCase(
        '^import\\b',
        ['import os', 'import statistics', 'import subprocess', 'import sys', 'import time'],
    ),
    TestCase(
        ';$',
        ['};', 'std::mutex outputMutex;', 'using Pattern = std::unique_ptr<pcre2_code, decltype(&pcre2_code_free)>;', '    int errcode;', '    PCRE2_SIZE erroffset;', '                                   PCRE2_ZERO_TERMINATED, PCRE2_MULTILINE, &errcode, &erroffset, nullptr);', '        PCRE2_UCHAR msg[256];', '        pcre2_get_error_message(errcode, msg, sizeof(msg));', '        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));', '    pcre2_jit_compile(re, PCRE2_JIT_COMPLETE);', '    return Pattern(re, pcre2_code_free);', '    std::ifstream file(path, std::ios::binary);', '        std::lock_guard<std::mutex> lock(outputMutex);', '        std::cerr << path.string() << ": Failed to open\\n";', '        return;', '    file.seekg(0, std::ios::end);', '    const std::streamoff size = file.tellg();', '    file.seekg(0, std::ios::beg);', '    buf.resize(static_cast<size_t>(size));', '    const std::streamsize probe = size < 8192 ? size : 8192;', '    file.read(buf.data(), probe);', '    size_t got = static_cast<size_t>(file.gcount());', '        file.read(buf.data() + got, size - static_cast<std::streamoff>(got));', '        got += static_cast<size_t>(file.gcount());', '        size_t write = 0;', '            buf[write++] = buf[read];', '        got = write;', '        pcre2_match_data_create_from_pattern(expression, nullptr), pcre2_match_data_free);', '    out.clear();', '    PCRE2_SIZE* ovector = pcre2_get_ovector_pointer(matchData.get());', '    size_t pos = 0;', '                             got, pos, 0, matchData.get(), nullptr);', '        const size_t matchStart = static_cast<size_t>(ovector[0]);', '        const size_t matchEnd   = static_cast<size_t>(ovector[1]);', "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", '        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;', "        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\\n', got - lineStart));", '        const size_t lineEnd = newline ? static_cast<size_t>(newline - buf.data()) : got;', '        bool matched = true;', '                                  lineEnd - lineStart, 0, 0, matchData.get(), nullptr) >= 0;', '            out.append(buf.data() + lineStart, lineEnd - lineStart);', "            out.push_back('\\n');", '        pos = lineEnd + 1;', '        std::lock_guard<std::mutex> lock(outputMutex);', '        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));', '    return;', '    std::vector<std::filesystem::path> files;', '    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);', '        const auto& entry = *it;', '            const std::string fileName = entry.path().filename().string();', '                it.disable_recursion_pending();', '            continue;', '            files.push_back(entry.path());', '    return files;', '        std::cerr << "usage: grep <path> <pattern>\\n";', '        return 2;', '    std::filesystem::path dir = std::filesystem::current_path();', '    dir /= argv[1];', '    Pattern expression = compileRegexPattern(argv[2]);', '        std::string buf, out;', '        grepFile(dir, expression.get(), buf, out);', '        return 0;', '    const std::vector<std::filesystem::path> files = collectFiles(dir);', '    unsigned threadCount = std::thread::hardware_concurrency();', '    std::atomic<size_t> nextFile{0};', '    std::vector<std::thread> threads;', '    threads.reserve(threadCount);', '            std::string buf, out;', '                const size_t i = nextFile.fetch_add(1, std::memory_order_relaxed);', '                    grepFile(files[i], expression.get(), buf, out);', '                    std::lock_guard<std::mutex> lock(outputMutex);', '                    std::cerr << files[i].string() << ": " << e.what() << "\\n";', '        });', '        thread.join();', '    return 0;'],
    ),
    TestCase(
        '^\\}',
        ['};', '}', '}', '}', '}'],
    ),
    TestCase(
        '^#\\s*include',
        ['#include <pcre2.h>', '#include <iostream>', '#include <filesystem>', '#include <fstream>', '#include <memory>', '#include <string>', '#include <vector>', '#include <algorithm>', '#include <array>', '#include <cstring>', '#include <string_view>', '#include <thread>', '#include <mutex>', '#include <atomic>'],
    ),
    TestCase(
        '[\\w.]+::',
        ['constexpr std::array<std::string_view, 6> ignoredFolders{', 'std::mutex outputMutex;', 'using Pattern = std::unique_ptr<pcre2_code, decltype(&pcre2_code_free)>;', '        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));', 'void grepFile(const std::filesystem::path& path, const pcre2_code* expression,', '              std::string& buf, std::string& out) {', '    std::ifstream file(path, std::ios::binary);', '        std::lock_guard<std::mutex> lock(outputMutex);', '        std::cerr << path.string() << ": Failed to open\\n";', '    file.seekg(0, std::ios::end);', '    const std::streamoff size = file.tellg();', '    file.seekg(0, std::ios::beg);', '    const std::streamsize probe = size < 8192 ? size : 8192;', "    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", '    if (static_cast<std::streamoff>(got) < size) {', '        file.read(buf.data() + got, size - static_cast<std::streamoff>(got));', "    if (std::memchr(buf.data(), '\\r', got) != nullptr) {", '    std::unique_ptr<pcre2_match_data, decltype(&pcre2_match_data_free)> matchData(', '        if (rc < 0) { throw std::runtime_error("Match error: " + std::to_string(rc)); }', "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", '        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;', "        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\\n', got - lineStart));", '        std::lock_guard<std::mutex> lock(outputMutex);', '        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));', 'std::vector<std::filesystem::path> collectFiles(const std::filesystem::path& dir) {', '    std::vector<std::filesystem::path> files;', '    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);', '        it != std::filesystem::recursive_directory_iterator(); ++it) {', '            const std::string fileName = entry.path().filename().string();', '            if (fileName.starts_with(".") || std::ranges::find(ignoredFolders, fileName) != ignoredFolders.end()) {', '        std::cerr << "usage: grep <path> <pattern>\\n";', '    std::filesystem::path dir = std::filesystem::current_path();', '    if (std::filesystem::is_regular_file(dir)) {', '        std::string buf, out;', '    const std::vector<std::filesystem::path> files = collectFiles(dir);', '    unsigned threadCount = std::thread::hardware_concurrency();', '    std::atomic<size_t> nextFile{0};', '    std::vector<std::thread> threads;', '            std::string buf, out;', '                const size_t i = nextFile.fetch_add(1, std::memory_order_relaxed);', '                catch (const std::exception& e) {', '                    std::lock_guard<std::mutex> lock(outputMutex);', '                    std::cerr << files[i].string() << ": " << e.what() << "\\n";'],
    ),
    TestCase(
        '[&|]{2}',
        ["            if (buf[read] == '\\r' && read + 1 < got && buf[read + 1] == '\\n') { continue; }", '            if (fileName.starts_with(".") || std::ranges::find(ignoredFolders, fileName) != ignoredFolders.end()) {'],
    ),
    TestCase(
        '[$^]',
        ['set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")'],
    ),
    TestCase(
        '(int|size_t|char)\\s+\\w+',
        ['    int errcode;', '    size_t got = static_cast<size_t>(file.gcount());', '        size_t write = 0;', '        for (size_t read = 0; read < got; ++read) {', '    size_t pos = 0;', '        int rc = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(buf.data()),', '        const size_t matchStart = static_cast<size_t>(ovector[0]);', '        const size_t matchEnd   = static_cast<size_t>(ovector[1]);', "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", '        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;', '        const size_t lineEnd = newline ? static_cast<size_t>(newline - buf.data()) : got;', 'int main(int argc, char* argv[]) {', '                const size_t i = nextFile.fetch_add(1, std::memory_order_relaxed);'],
    ),
    TestCase(
        '^(if|for|while)\\b',
        ['for d in (SMALL, LARGE):', 'if not GNU:', 'for size, path, kind, pat in CASES:', 'for size, kind, pat, res in rows:'],
    ),
    TestCase(
        '\\b(true|false|nullptr)\\b',
        ['                                   PCRE2_ZERO_TERMINATED, PCRE2_MULTILINE, &errcode, &erroffset, nullptr);', '    if (re == nullptr) {', "    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", "    if (std::memchr(buf.data(), '\\r', got) != nullptr) {", '        pcre2_match_data_create_from_pattern(expression, nullptr), pcre2_match_data_free);', '                             got, pos, 0, matchData.get(), nullptr);', '        bool matched = true;', '                                  lineEnd - lineStart, 0, 0, matchData.get(), nullptr) >= 0;'],
    ),
    TestCase(
        '\\b(?:int|long|short)\\b.*\\b(?:int|long|short)\\b',
        ['int main(int argc, char* argv[]) {'],
    ),
    TestCase(
        '(\\w)(\\w)\\2\\1',
        ['#include <array>', 'constexpr std::array<std::string_view, 6> ignoredFolders{', '    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);'],
    ),
    TestCase(
        '(?<=#include )<\\w+>',
        ['#include <iostream>', '#include <filesystem>', '#include <fstream>', '#include <memory>', '#include <string>', '#include <vector>', '#include <algorithm>', '#include <array>', '#include <cstring>', '#include <string_view>', '#include <thread>', '#include <mutex>', '#include <atomic>'],
    ),
    TestCase(
        '(?<![\\w])size_t(?![\\w])',
        ['    buf.resize(static_cast<size_t>(size));', '    size_t got = static_cast<size_t>(file.gcount());', '        got += static_cast<size_t>(file.gcount());', '        size_t write = 0;', '        for (size_t read = 0; read < got; ++read) {', '    size_t pos = 0;', '        const size_t matchStart = static_cast<size_t>(ovector[0]);', '        const size_t matchEnd   = static_cast<size_t>(ovector[1]);', "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", '        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;', '        const size_t lineEnd = newline ? static_cast<size_t>(newline - buf.data()) : got;', '    std::atomic<size_t> nextFile{0};', '                const size_t i = nextFile.fetch_add(1, std::memory_order_relaxed);'],
    ),
    TestCase(
        '(?i)cmake(?-i:_minimum)',
        ['cmake_minimum_required(VERSION 3.28)'],
    ),
    TestCase(
        '\\Q{{config}}\\E',
        ['    cmake --build build --config {{config}}', '    cmake --build build --config {{config}}', '    powershell -Command "./build/{{config}}/grep.exe . conf"'],
    ),
    TestCase(
        'import \\Kos',
        ['import os'],
    ),
    TestCase(
        '^(?:(?:a|b)*)$',
        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    ),
    TestCase(
        'std::\\w+<\\w+(::\\w+)*>',
        ['        std::lock_guard<std::mutex> lock(outputMutex);', '        std::lock_guard<std::mutex> lock(outputMutex);', 'std::vector<std::filesystem::path> collectFiles(const std::filesystem::path& dir) {', '    std::vector<std::filesystem::path> files;', '    const std::vector<std::filesystem::path> files = collectFiles(dir);', '    std::atomic<size_t> nextFile{0};', '    std::vector<std::thread> threads;', '                    std::lock_guard<std::mutex> lock(outputMutex);'],
    ),
    TestCase(
        '::\\w+\\(',
        ['        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));', "    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", "    if (std::memchr(buf.data(), '\\r', got) != nullptr) {", '        if (rc < 0) { throw std::runtime_error("Match error: " + std::to_string(rc)); }', "        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\\n', got - lineStart));", '    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);', '        it != std::filesystem::recursive_directory_iterator(); ++it) {', '            if (fileName.starts_with(".") || std::ranges::find(ignoredFolders, fileName) != ignoredFolders.end()) {', '    std::filesystem::path dir = std::filesystem::current_path();', '    if (std::filesystem::is_regular_file(dir)) {', '    unsigned threadCount = std::thread::hardware_concurrency();'],
    ),
    TestCase(
        '\\bthrow\\b',
        ['        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));', '        if (rc < 0) { throw std::runtime_error("Match error: " + std::to_string(rc)); }'],
    ),
    TestCase(
        '\\bconst\\b.*&',
        ['void grepFile(const std::filesystem::path& path, const pcre2_code* expression,', 'std::vector<std::filesystem::path> collectFiles(const std::filesystem::path& dir) {', '        const auto& entry = *it;', '                catch (const std::exception& e) {'],
    ),
    TestCase(
        '\\bauto\\b',
        ['    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);', '        const auto& entry = *it;', '    for (auto& thread : threads) {'],
    ),
    TestCase(
        'static_cast<[^>]+>',
        ['    buf.resize(static_cast<size_t>(size));', '    size_t got = static_cast<size_t>(file.gcount());', '    if (static_cast<std::streamoff>(got) < size) {', '        file.read(buf.data() + got, size - static_cast<std::streamoff>(got));', '        got += static_cast<size_t>(file.gcount());', '        const size_t matchStart = static_cast<size_t>(ovector[0]);', '        const size_t matchEnd   = static_cast<size_t>(ovector[1]);', "        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\\n', got - lineStart));", '        const size_t lineEnd = newline ? static_cast<size_t>(newline - buf.data()) : got;', '        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));'],
    ),
    TestCase(
        '\\bset\\(\\w+',
        ['set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")', 'set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_PCRE2_8 ON CACHE BOOL "" FORCE)', 'set(PCRE2_SUPPORT_JIT ON CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_PCRE2GREP OFF CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_TESTS OFF CACHE BOOL "" FORCE)'],
    ),
    TestCase(
        '^\\w+:$',
        ['configure:'],
    ),
    TestCase(
        '^\\s+@\\w+$',
        ['    @clear', '    @clear', '    @clear'],
    ),
    TestCase(
        '^\\|[-:|]+\\|?$',
        ['|---|---|---:|---:|---:|'],
    ),
    TestCase(
        '\\[.*\\]\\(.*\\)',
        ['Median of 20 warm-cache runs. All greps skip binary files. ([Bench Script](bench.py))'],
    ),
    TestCase(
        '^```\\w*$',
        ['```bash', '```'],
    ),
    TestCase(
        '\\bdef \\w+\\(.*\\):',
        ['def cmds(path, pat):', 'def timed(cmd):'],
    ),
    TestCase(
        '^\\s*(?:for|if|while) .*:$',
        ['for d in (SMALL, LARGE):', '    if not os.path.isdir(d):', 'if not GNU:', 'for size, path, kind, pat in CASES:', '    for name, cmd in cmds(path, pat).items():', 'for size, kind, pat, res in rows:'],
    ),
    TestCase(
        'f\\"[^\\"]*\\{',
        ['        sys.exit(f"Directory not found: {d}")', '        print(f"{size} {kind} {name}: {res[name]:.0f} ms, {lines} lines", flush=True)', '        f"**{res[n]:.0f} ms**" if res[n] == best else f"{res[n]:.0f} ms" for n in names', '    print(f"| {size} | {kind} `{pat}` | " + " | ".join(cells) + " |")'],
    ),
    TestCase(
        '\\bos\\.path\\.\\w+',
        ['MINE = os.path.join(', '    os.path.dirname(os.path.abspath(__file__)), "build", "Release", "grep.exe"', '            if os.path.isfile(p)), None)', '    if not os.path.isdir(d):'],
    ),
    TestCase(
        '"""',
        ['"""Benchmark this grep against ripgrep and GNU grep. Usage: python bench.py [--fast]"""'],
    ),
    TestCase(
        '\\bTrue\\b|\\bFalse\\b',
        ['print(subprocess.run([GNU, "--version"], capture_output=True, text=True, check=False).stdout.splitlines()[0])', '    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)', '        lines = subprocess.run(cmd, capture_output=True, check=False).stdout.count(b"\\n")', '        print(f"{size} {kind} {name}: {res[name]:.0f} ms, {lines} lines", flush=True)'],
    ),
    TestCase(
        '\\bNone\\b',
        ['            if os.path.isfile(p)), None)'],
    ),
    TestCase(
        '^import (?:os|sys)$',
        ['import os', 'import sys'],
    ),
    TestCase(
        '^MINE\\b',
        ['MINE = os.path.join('],
    ),
    TestCase(
        '^RG = ',
        ['RG = "rg"'],
    ),
    TestCase(
        '^GNU = ',
        ['GNU = next((p for p in (r"C:\\msys64\\ucrt64\\bin\\grep.exe", r"C:\\Program Files\\Git\\usr\\bin\\grep.exe")'],
    ),
    TestCase(
        '^SMALL = r',
        ['SMALL = r"C:\\Program Files (x86)\\Microsoft Visual Studio\\18\\BuildTools\\VC\\Tools\\MSVC\\14.51.36231\\include"'],
    ),
    TestCase(
        '^LARGE = r',
        ['LARGE = r"C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0"'],
    ),
    TestCase(
        '\\bRUNS\\b',
        ['RUNS = 1 if "--fast" in sys.argv else 20', '        res[name] = statistics.median(timed(cmd) for _ in range(RUNS))'],
    ),
    TestCase(
        '^\\s+\\(\\"(Small|Large)\\"',
        ['    ("Small", SMALL, "literal", "constexpr"),', '    ("Small", SMALL, "regex", "_[A-Z]+_[A-Z]+[(]"),', '    ("Small", SMALL, "no match", "zqxjvk"),', '    ("Large", LARGE, "literal", "HRESULT"),', '    ("Large", LARGE, "regex", "_[A-Z]+_[A-Z]+[(]"),', '    ("Large", LARGE, "no match", "zqxjvk"),'],
    ),
    TestCase(
        '^for \\w+ in',
        ['for d in (SMALL, LARGE):'],
    ),
    TestCase(
        '^rows = ',
        ['rows = []'],
    ),
    TestCase(
        '^def \\w+\\(\\w+, \\w+\\):$',
        ['def cmds(path, pat):'],
    ),
    TestCase(
        '^project\\(\\w+ LANGUAGES \\w+\\)$',
        ['project(grep LANGUAGES CXX)'],
    ),
    TestCase(
        '^set\\(\\w+ \\w+ CACHE BOOL \\"\\" FORCE\\)$',
        ['set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_PCRE2_8 ON CACHE BOOL "" FORCE)', 'set(PCRE2_SUPPORT_JIT ON CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_PCRE2GREP OFF CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_TESTS OFF CACHE BOOL "" FORCE)'],
    ),
    TestCase(
        '^set\\(PCRE2_\\w+ (ON|OFF)',
        ['set(PCRE2_BUILD_PCRE2_8 ON CACHE BOOL "" FORCE)', 'set(PCRE2_SUPPORT_JIT ON CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_PCRE2GREP OFF CACHE BOOL "" FORCE)', 'set(PCRE2_BUILD_TESTS OFF CACHE BOOL "" FORCE)'],
    ),
    TestCase(
        'GIT_TAG pcre2-[\\d.]+',
        ['    GIT_TAG pcre2-10.47'],
    ),
    TestCase(
        '^FetchContent_\\w+\\(',
        ['FetchContent_Declare(', 'FetchContent_MakeAvailable(pcre2)'],
    ),
    TestCase(
        '^add_executable\\(\\w+ [\\w/.]+\\)$',
        ['add_executable(grep src/main.cpp)'],
    ),
    TestCase(
        '^target_\\w+\\(\\w+ PRIVATE',
        ['target_compile_features(grep PRIVATE cxx_std_20)', 'target_link_libraries(grep PRIVATE pcre2-8)'],
    ),
    TestCase(
        'cxx_std_\\d+',
        ['target_compile_features(grep PRIVATE cxx_std_20)'],
    ),
    TestCase(
        '\\bpcre2-8\\b',
        ['target_link_libraries(grep PRIVATE pcre2-8)'],
    ),
    TestCase(
        '^build/$',
        ['build/'],
    ),
    TestCase(
        '^(build|run) config=\\"\\w+\\":$',
        ['build config="Release":', 'run config="Release":'],
    ),
    TestCase(
        '^\\s+cmake -B build$',
        ['    cmake -B build'],
    ),
    TestCase(
        'powershell -Command \\"[^\\"]*\\"$',
        ['    powershell -Command "if (Test-Path \'build\') { Remove-Item -Path \'build\' -Recurse -Force }"', '    powershell -Command "./build/{{config}}/grep.exe . conf"'],
    ),
    TestCase(
        '^# Grep$',
        ['# Grep'],
    ),
    TestCase(
        '^## \\w+( and \\w+)?$',
        ['## Install and Run'],
    ),
    TestCase(
        '~\\d+x',
        ['A simple grep tool written in C++20, ~3x faster than GNU grep and matches ripgrep on small folders.'],
    ),
    TestCase(
        '^\\| (Small|Large) \\| (literal|regex|no match) ',
        ['| Small | literal `constexpr` | **16 ms** | 23 ms | 110 ms |', '| Small | regex `_[A-Z]+_[A-Z]+[(]` | **18 ms** | 25 ms | 158 ms |', '| Small | no match `zqxjvk` | **16 ms** | 23 ms | 111 ms |', '| Large | literal `HRESULT` | 183 ms | **123 ms** | 1587 ms |', '| Large | regex `_[A-Z]+_[A-Z]+[(]` | 172 ms | **138 ms** | 2101 ms |', '| Large | no match `zqxjvk` | 167 ms | **118 ms** | 1782 ms |'],
    ),
    TestCase(
        '\\(8C/16T\\)',
        ['## Benchmarks (Windows 11, Ryzen 7 5700G (8C/16T))'],
    ),
    TestCase(
        'git clone https://\\S+$',
        ['git clone https://github.com/Optccopa/Grep'],
    ),
    TestCase(
        '^#define \\w+ \\d+$',
        ['#define PCRE2_CODE_UNIT_WIDTH 8'],
    ),
    TestCase(
        '^\\s+\\"\\w+\\"(,|$)',
        ['    "node_modules",', '    "build",', '    "out",', '    "dist",', '    "obj",', '    "__pycache__"'],
    ),
    TestCase(
        '^using \\w+ = ',
        ['using Pattern = std::unique_ptr<pcre2_code, decltype(&pcre2_code_free)>;'],
    ),
    TestCase(
        '^std::mutex \\w+;$',
        ['std::mutex outputMutex;'],
    ),
    TestCase(
        '\\bPCRE2_(?:ZERO_TERMINATED|MULTILINE|JIT_COMPLETE)\\b',
        ['                                   PCRE2_ZERO_TERMINATED, PCRE2_MULTILINE, &errcode, &erroffset, nullptr);', '    pcre2_jit_compile(re, PCRE2_JIT_COMPLETE);'],
    ),
    TestCase(
        'static_cast<(size_t|std::streamsize|std::streamoff)>',
        ['    buf.resize(static_cast<size_t>(size));', '    size_t got = static_cast<size_t>(file.gcount());', '    if (static_cast<std::streamoff>(got) < size) {', '        file.read(buf.data() + got, size - static_cast<std::streamoff>(got));', '        got += static_cast<size_t>(file.gcount());', '        const size_t matchStart = static_cast<size_t>(ovector[0]);', '        const size_t matchEnd   = static_cast<size_t>(ovector[1]);', '        const size_t lineEnd = newline ? static_cast<size_t>(newline - buf.data()) : got;', '        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));'],
    ),
    TestCase(
        'reinterpret_cast<PCRE2_SPTR>',
        ['    pcre2_code* re = pcre2_compile(reinterpret_cast<PCRE2_SPTR>(pattern),', '        int rc = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(buf.data()),', '            matched = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(buf.data() + lineStart),'],
    ),
    TestCase(
        'std::lock_guard<std::mutex> lock\\(\\w+\\);',
        ['        std::lock_guard<std::mutex> lock(outputMutex);', '        std::lock_guard<std::mutex> lock(outputMutex);', '                    std::lock_guard<std::mutex> lock(outputMutex);'],
    ),
    TestCase(
        'std::memchr\\(',
        ["    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", "    if (std::memchr(buf.data(), '\\r', got) != nullptr) {", "        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\\n', got - lineStart));"],
    ),
    TestCase(
        '^\\s+if \\(.*\\) \\{ (return|break)[^}]*\\}$',
        ['    if (size <= 0) { return; }', '    if (got == 0) { return; }', "    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", '        if (rc == PCRE2_ERROR_NOMATCH) { break; }', '                if (i >= files.size()) { break; }'],
    ),
    TestCase(
        '^\\s+for \\(;;\\) \\{$',
        ['            for (;;) {'],
    ),
    TestCase(
        '\\b8192\\b',
        ['    const std::streamsize probe = size < 8192 ? size : 8192;'],
    ),
    TestCase(
        "'\\\\0'|'\\\\r'|'\\\\n'",
        ["    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", "    if (std::memchr(buf.data(), '\\r', got) != nullptr) {", "            if (buf[read] == '\\r' && read + 1 < got && buf[read + 1] == '\\n') { continue; }", "        const size_t previous  = matchStart ? buf.rfind('\\n', matchStart - 1) : std::string::npos;", "        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\\n', got - lineStart));", "            out.push_back('\\n');"],
    ),
    TestCase(
        '\\bnullptr\\b',
        ['                                   PCRE2_ZERO_TERMINATED, PCRE2_MULTILINE, &errcode, &erroffset, nullptr);', '    if (re == nullptr) {', "    if (std::memchr(buf.data(), '\\0', got) != nullptr) { return; }", "    if (std::memchr(buf.data(), '\\r', got) != nullptr) {", '        pcre2_match_data_create_from_pattern(expression, nullptr), pcre2_match_data_free);', '                             got, pos, 0, matchData.get(), nullptr);', '                                  lineEnd - lineStart, 0, 0, matchData.get(), nullptr) >= 0;'],
    ),
    TestCase(
        '\\bconst auto&',
        ['        const auto& entry = *it;'],
    ),
    TestCase(
        '\\bunsigned \\w+',
        ['    unsigned threadCount = std::thread::hardware_concurrency();', '    for (unsigned t = 0; t < threadCount; ++t) {'],
    ),
    TestCase(
        'a{2}',
        [],
    ),
    TestCase(
        '^\\t',
        [],
    ),
    TestCase(
        '\\s$',
        [],
    ),
    TestCase(
        '[[:space:]]+$',
        [],
    ),
    TestCase(
        '\\p{Ll}{15,}',
        [],
    ),
    TestCase(
        '[\\x00-\\x08]',
        [],
    ),
    TestCase(
        '\\xa0',
        [],
    ),
    TestCase(
        '[^\\x00-\\x7f]',
        [],
    ),
    TestCase(
        '[.]{2}',
        [],
    ),
    TestCase(
        '^(a|ab)(c|bcd)(d*)$',
        [],
    ),
    TestCase(
        '^(\\w+)\\s.*\\1$',
        [],
    ),
    TestCase(
        '\\Q(c)\\E',
        [],
    ),
    TestCase(
        '\\e',
        [],
    ),
    TestCase(
        '\\a',
        [],
    ),
    TestCase(
        '\\cI',
        [],
    ),
    TestCase(
        '".*+"',
        [],
    ),
    TestCase(
        'x*+x',
        [],
    ),
    TestCase(
        '\\v',
        [],
    ),
    TestCase(
        '=\\s*\\{.*\\};',
        [],
    ),
    TestCase(
        '/\\*',
        [],
    ),
    TestCase(
        '\\b0x[0-9a-fA-F]+\\b',
        [],
    ),
    TestCase(
        '\\bstd::move\\b',
        [],
    ),
    TestCase(
        '%\\w',
        [],
    ),
    TestCase(
        '(?>[^\\n]*)\\)$',
        [],
    ),
    TestCase(
        '[0-9]+ \\* \\d+|\\d+ \\*',
        [],
    ),
]
