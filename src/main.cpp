#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>

#include <iostream>
#include <filesystem>
#include <fstream>
#include <memory>

#include <string>
#include <vector>
#include <algorithm>
#include <array>
#include <cstring>
#include <string_view>
#include <thread>
#include <mutex>
#include <atomic>

constexpr std::array<std::string_view, 6> ignoredFolders{
    "node_modules",
    "build",
    "out",
    "dist",
    "obj",
    "__pycache__"
    // also folders starting in .
};

std::mutex outputMutex;

using Pattern = std::unique_ptr<pcre2_code, decltype(&pcre2_code_free)>;

Pattern compileRegexPattern(char* pattern) {
    // the whole file is one subject, so these would anchor to the file, not the line
    for (const char* c = pattern; *c && c[1]; ++c) {
        // (?-m) and (?^) would make ^ and $ match the file's ends instead of each line's
        if (c[0] == '(' && c[1] == '?') {
            const char* flags = c + 2;
            const size_t len = std::strcspn(flags, ":)");
            const std::string_view group(flags, len);
            const size_t off = group.find_first_of("-^");
            const bool isFlagGroup = group.find_first_not_of("imnsxJU-^") == std::string_view::npos;
            if (isFlagGroup && off != std::string_view::npos && (group[off] == '^' || group.find('m', off) != std::string_view::npos)) {
                throw std::runtime_error("Unsupported flag (?-m), ^ and $ always match per line");
            }
        }
        if (*c != '\\') { continue; }
        if (std::strchr("AzZG", c[1])) {
            throw std::runtime_error("Unsupported anchor \\" + std::string(1, c[1]) + ", use ^ and $");
        }
        ++c;
    }

    int errcode;
    PCRE2_SIZE erroffset;
    pcre2_code* re = pcre2_compile(reinterpret_cast<PCRE2_SPTR>(pattern),
                                   PCRE2_ZERO_TERMINATED, PCRE2_MULTILINE, &errcode, &erroffset, nullptr);

    if (re == nullptr) {
        PCRE2_UCHAR msg[256];
        pcre2_get_error_message(errcode, msg, sizeof(msg));
        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));
    }

    pcre2_jit_compile(re, PCRE2_JIT_COMPLETE);

    return Pattern(re, pcre2_code_free);
}

void grepFile(const std::filesystem::path& path, const pcre2_code* expression,
              std::string& buf, std::string& out) {
    std::ifstream file(path, std::ios::binary);

    if (!file.is_open()) {
        std::lock_guard<std::mutex> lock(outputMutex);
        std::cerr << path.string() << ": Failed to open\n";
        return;
    }

    file.seekg(0, std::ios::end);
    const std::streamoff size = file.tellg();
    file.seekg(0, std::ios::beg);

    if (size <= 0) { return; }

    buf.resize(static_cast<size_t>(size));

    const std::streamsize probe = size < 8192 ? size : 8192;
    file.read(buf.data(), probe);
    size_t got = static_cast<size_t>(file.gcount());

    if (got == 0) { return; }
    if (std::memchr(buf.data(), '\0', got) != nullptr) { return; }

    if (static_cast<std::streamoff>(got) < size) {
        file.read(buf.data() + got, size - static_cast<std::streamoff>(got));
        got += static_cast<size_t>(file.gcount());
    }

    if (std::memchr(buf.data(), '\r', got) != nullptr) {
        size_t write = 0;
        for (size_t read = 0; read < got; ++read) {
            if (buf[read] == '\r' && read + 1 < got && buf[read + 1] == '\n') { continue; }
            buf[write++] = buf[read];
        }
        got = write;
    }

    std::unique_ptr<pcre2_match_data, decltype(&pcre2_match_data_free)> matchData(
        pcre2_match_data_create_from_pattern(expression, nullptr), pcre2_match_data_free);

    out.clear();

    PCRE2_SIZE* ovector = pcre2_get_ovector_pointer(matchData.get());

    size_t pos = 0;
    while (pos <= got) {
        int rc = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(buf.data()),
                             got, pos, 0, matchData.get(), nullptr);

        if (rc == PCRE2_ERROR_NOMATCH) { break; }
        if (rc < 0) { throw std::runtime_error("Match error: " + std::to_string(rc)); }

        const size_t matchStart = static_cast<size_t>(ovector[0]);
        const size_t matchEnd   = static_cast<size_t>(ovector[1]);

        if (matchStart == got && got > 0 && buf[got - 1] == '\n') { break; }

        const size_t previous  = matchStart ? buf.rfind('\n', matchStart - 1) : std::string::npos;
        const size_t lineStart = (previous == std::string::npos) ? 0 : previous + 1;

        const char* newline = static_cast<const char*>(std::memchr(buf.data() + lineStart, '\n', got - lineStart));
        const size_t lineEnd = newline ? static_cast<size_t>(newline - buf.data()) : got;

        bool matched = true;
        if (matchEnd > lineEnd) {
            matched = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(buf.data() + lineStart),
                                  lineEnd - lineStart, 0, 0, matchData.get(), nullptr) >= 0;
        }

        if (matched) {
            out.append(buf.data() + lineStart, lineEnd - lineStart);
            out.push_back('\n');
        }

        pos = lineEnd + 1;
    }

    if (!out.empty()) {
        std::lock_guard<std::mutex> lock(outputMutex);
        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));
    }
    return;
}

std::vector<std::filesystem::path> collectFiles(const std::filesystem::path& dir) {
    std::vector<std::filesystem::path> files;

    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);
        it != std::filesystem::recursive_directory_iterator(); ++it) {

        const auto& entry = *it;

        if (entry.is_directory()) {
            const std::string fileName = entry.path().filename().string();
            if (fileName.starts_with(".") || std::ranges::find(ignoredFolders, fileName) != ignoredFolders.end()) {
                it.disable_recursion_pending();
            }
            continue;
        }

        if (entry.is_regular_file()) {
            files.push_back(entry.path());
        }
    }

    return files;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "usage: grep <path> <pattern>\n";
        return 2;
    }

    std::filesystem::path dir = std::filesystem::current_path();
    dir /= argv[1];

    Pattern expression = compileRegexPattern(argv[2]);

    if (std::filesystem::is_regular_file(dir)) {
        std::string buf, out;
        grepFile(dir, expression.get(), buf, out);
        return 0;
    }

    const std::vector<std::filesystem::path> files = collectFiles(dir);

    unsigned threadCount = std::thread::hardware_concurrency();
    if (threadCount == 0) { threadCount = 4; }

    std::atomic<size_t> nextFile{0};
    std::vector<std::thread> threads;
    threads.reserve(threadCount);

    for (unsigned t = 0; t < threadCount; ++t) {
        threads.emplace_back([&] {
            std::string buf, out;
            for (;;) {
                const size_t i = nextFile.fetch_add(1, std::memory_order_relaxed);
                if (i >= files.size()) { break; }

                try {
                    grepFile(files[i], expression.get(), buf, out);
                }
                catch (const std::exception& e) {
                    std::lock_guard<std::mutex> lock(outputMutex);
                    std::cerr << files[i].string() << ": " << e.what() << "\n";
                }
            }
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }

    return 0;
}