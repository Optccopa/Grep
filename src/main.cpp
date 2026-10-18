#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>

#include <fcntl.h>
#include <io.h>

#include <iostream>
#include <filesystem>
#include <memory>

#include <string>
#include <vector>
#include <algorithm>
#include <array>
#include <cstring>
#include <string_view>
#include <thread>
#include <future>
#include <mutex>

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
std::string_view literal;

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
    pcre2_compile_context* context = pcre2_compile_context_create(nullptr);
    pcre2_set_newline(context, PCRE2_NEWLINE_ANYCRLF);
    pcre2_code* re = pcre2_compile(reinterpret_cast<PCRE2_SPTR>(pattern),
                                   PCRE2_ZERO_TERMINATED, PCRE2_MULTILINE | PCRE2_USE_OFFSET_LIMIT, &errcode, &erroffset, context);
    pcre2_compile_context_free(context);

    if (re == nullptr) {
        PCRE2_UCHAR msg[256];
        pcre2_get_error_message(errcode, msg, sizeof(msg));
        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));
    }

    pcre2_jit_compile(re, PCRE2_JIT_COMPLETE);

    return Pattern(re, pcre2_code_free);
}

void grepChunk(const char* data, size_t size, size_t start, size_t end, const pcre2_code* expression, std::string& out) {
    std::unique_ptr<pcre2_match_data, decltype(&pcre2_match_data_free)> matchData(
        pcre2_match_data_create_from_pattern(expression, nullptr), pcre2_match_data_free);
    std::unique_ptr<pcre2_match_context, decltype(&pcre2_match_context_free)> matchContext(
        pcre2_match_context_create(nullptr), pcre2_match_context_free);
    pcre2_set_offset_limit(matchContext.get(), end);

    PCRE2_SIZE* ovector = pcre2_get_ovector_pointer(matchData.get());
    const std::string_view text(data, end);

    size_t pos = start;
    while (pos < end) {
        size_t matchStart, matchEnd;
        if (!literal.empty()) {
            matchStart = text.find(literal, pos);
            if (matchStart == std::string_view::npos) { break; }
            matchEnd = matchStart + literal.size();
        } else {
            const int rc = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(data),
                                       size, pos, 0, matchData.get(), matchContext.get());
            if (rc == PCRE2_ERROR_NOMATCH) { break; }
            if (rc < 0) { throw std::runtime_error("Match error: " + std::to_string(rc)); }
            matchStart = static_cast<size_t>(ovector[0]);
            matchEnd   = static_cast<size_t>(ovector[1]);
        }

        if (matchStart == end && data[end - 1] == '\n') { break; }

        const size_t previous  = matchStart ? text.rfind('\n', matchStart - 1) : std::string_view::npos;
        const size_t lineStart = (previous == std::string_view::npos) ? 0 : previous + 1;

        const char* newline = static_cast<const char*>(std::memchr(data + lineStart, '\n', end - lineStart));
        const size_t lineEnd = newline ? static_cast<size_t>(newline - data) : end;
        const size_t trimmed = (lineEnd > lineStart && data[lineEnd - 1] == '\r') ? lineEnd - 1 : lineEnd;

        bool matched = true;
        if (matchEnd > trimmed) {
            matched = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(data + lineStart),
                                  trimmed - lineStart, 0, 0, matchData.get(), nullptr) >= 0;
        }

        if (matched) {
            out.append(data + lineStart, trimmed - lineStart);
            out.push_back('\n');
        }

        pos = lineEnd + 1;
    }
}

using View = std::unique_ptr<const char, decltype(&UnmapViewOfFile)>;

View mapView(HANDLE mapping) {
    return View(static_cast<const char*>(MapViewOfFile(mapping, FILE_MAP_READ, 0, 0, 0)), UnmapViewOfFile);
}

size_t lineAfter(const char* data, size_t size, size_t offset) {
    if (offset == 0) { return 0; }
    const char* newline = static_cast<const char*>(std::memchr(data + offset - 1, '\n', size - offset + 1));
    return newline ? static_cast<size_t>(newline - data) + 1 : size;
}

void grepChunks(HANDLE file, size_t size, size_t chunks, const pcre2_code* expression, std::vector<std::string>& outs) {
    const std::unique_ptr<void, decltype(&CloseHandle)> mapping(
        CreateFileMappingW(file, nullptr, PAGE_READONLY, 0, 0, nullptr), CloseHandle);
    if (!mapping) { return; }

    const View view = mapView(mapping.get());
    if (!view || std::memchr(view.get(), '\0', 8192) != nullptr) { return; }

    auto scan = [&](const char* data, size_t i) {
        grepChunk(data, size, lineAfter(data, size, size * i / chunks), lineAfter(data, size, size * (i + 1) / chunks),
                  expression, outs[i]);
    };

    std::vector<std::future<void>> helpers;
    for (size_t i = 1; i < chunks; ++i) {
        helpers.push_back(std::async(std::launch::async, [&, i] {
            const View own = mapView(mapping.get());
            if (!own) { throw std::runtime_error("Failed to map"); }
            scan(own.get(), i);
        }));
    }
    scan(view.get(), 0);
    for (auto& helper : helpers) { helper.get(); }
}

void grepFile(const std::filesystem::path& path, const pcre2_code* expression) {
    HANDLE file = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                              nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);

    if (file == INVALID_HANDLE_VALUE) {
        std::lock_guard<std::mutex> lock(outputMutex);
        std::cerr << path.string() << ": Failed to open\n";
        return;
    }

    const std::unique_ptr<void, decltype(&CloseHandle)> fileHandle(file, CloseHandle);

    LARGE_INTEGER fileSize;
    if (!GetFileSizeEx(file, &fileSize) || fileSize.QuadPart <= 0) { return; }
    const size_t size = static_cast<size_t>(fileSize.QuadPart);

    static const size_t cores = std::max(1u, std::thread::hardware_concurrency());
    const size_t chunks = std::clamp<size_t>(size >> 20, 1, cores);
    thread_local std::vector<std::string> outs;
    outs.resize(chunks);
    for (std::string& out : outs) { out.clear(); }

    if (chunks == 1) {
        thread_local std::string buf;
        buf.resize(size);

        DWORD bytesRead = 0;
        ReadFile(file, buf.data(), static_cast<DWORD>(std::min<size_t>(size, 8192)), &bytesRead, nullptr);
        size_t got = bytesRead;
        if (got == 0 || std::memchr(buf.data(), '\0', got) != nullptr) { return; }

        if (got < size) {
            ReadFile(file, buf.data() + got, static_cast<DWORD>(size - got), &bytesRead, nullptr);
            got += bytesRead;
        }
        grepChunk(buf.data(), got, 0, got, expression, outs[0]);
    } else {
        grepChunks(file, size, chunks, expression, outs);
    }

    if (std::ranges::all_of(outs, &std::string::empty)) { return; }
    std::lock_guard<std::mutex> lock(outputMutex);
    for (const std::string& out : outs) {
        std::cout.write(out.data(), static_cast<std::streamsize>(out.size()));
    }
}

void collectFiles(const std::filesystem::path& dir, std::vector<std::filesystem::path>& files, std::mutex& filesMutex) {
    for (auto it = std::filesystem::recursive_directory_iterator(
            dir,
            std::filesystem::directory_options::skip_permission_denied
        );
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
            std::lock_guard<std::mutex> lock(filesMutex);
            files.push_back(entry.path());
        }
    }
}

int main(int argc, char* argv[]) {
    // in text mode, the C runtime converts every \n to \r\n byte by byte.
    // That happens while the output mutex is held, so all 16 threads queue up behind it
    _setmode(_fileno(stdout), _O_BINARY);

    if (argc < 3) {
        std::cerr << "usage: grep <path> <pattern>\n";
        return 2;
    }

    std::filesystem::path dir = std::filesystem::current_path();
    dir /= argv[1];

    Pattern expression = compileRegexPattern(argv[2]);
    if (!std::strpbrk(argv[2], "\\^$.|?*+()[]{}")) { literal = argv[2]; }

    if (std::filesystem::is_regular_file(dir)) {
        grepFile(dir, expression.get());
        return 0;
    }

    std::vector<std::filesystem::path> files;
    std::mutex filesMutex;
    bool walked = false;
    size_t nextFile = 0;

    unsigned threadCount = std::thread::hardware_concurrency();
    if (threadCount == 0) { threadCount = 4; }

    std::vector<std::thread> threads;
    threads.reserve(threadCount);

    for (unsigned t = 0; t < threadCount; ++t) {
        threads.emplace_back([&] {
            for (;;) {
                std::filesystem::path path;
                {
                    std::lock_guard<std::mutex> lock(filesMutex);
                    if (nextFile < files.size()) { path = files[nextFile++]; }
                    else if (walked) { break; }
                }
                if (path.empty()) { std::this_thread::yield(); continue; }

                try {
                    grepFile(path, expression.get());
                }
                catch (const std::exception& e) {
                    std::lock_guard<std::mutex> lock(outputMutex);
                    std::cerr << path.string() << ": " << e.what() << "\n";
                }
            }
        });
    }

    collectFiles(dir, files, filesMutex);
    { std::lock_guard<std::mutex> lock(filesMutex); walked = true; }

    for (auto& thread : threads) {
        thread.join();
    }

    return 0;
}