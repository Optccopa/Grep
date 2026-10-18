#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>

#include <fcntl.h>
#include <io.h>

#include <iostream>
#include <fstream>
#include <filesystem>
#include <memory>

#include <string>
#include <vector>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstring>
#include <string_view>
#include <thread>
#include <future>
#include <mutex>

constexpr std::string_view usage =
    "usage: grep [flags] <path> <pattern>\n"
    "  -i         ignore case\n"
    "  -S         smart case: ignore case unless the pattern has an uppercase letter\n"
    "  -F         treat the pattern as a fixed string\n"
    "  -w         match whole words only\n"
    "  -x         match whole lines only\n"
    "  -v         print lines that do not match\n"
    "  -a         search binary files as text\n"
    "  -g GLOB    only search files matching GLOB, !GLOB excludes (repeatable)\n"
    "  -t TYPE    only search files of TYPE, -T TYPE excludes them (repeatable)\n"
    "  --hidden   search hidden files and folders\n"
    "  -u         don't respect .gitignore/.ignore, -uu also --hidden, -uuu also -a\n"
    "  --         end of flags";

constexpr std::array<std::pair<std::string_view, std::string_view>, 20> fileTypes{{
    {"c", "*.c *.h"},
    {"cpp", "*.cpp *.cc *.cxx *.c++ *.hpp *.hh *.hxx *.h++ *.h *.inl *.ixx"},
    {"cs", "*.cs *.csx"},
    {"go", "*.go"},
    {"java", "*.java"},
    {"js", "*.js *.mjs *.cjs *.jsx"},
    {"ts", "*.ts *.mts *.cts *.tsx"},
    {"py", "*.py *.pyi"},
    {"rust", "*.rs"},
    {"json", "*.json"},
    {"md", "*.md *.markdown"},
    {"yaml", "*.yaml *.yml"},
    {"toml", "*.toml"},
    {"cmake", "*.cmake CMakeLists.txt"},
    {"sh", "*.sh *.bash *.zsh"},
    {"ps", "*.ps1 *.psm1 *.psd1"},
    {"html", "*.html *.htm"},
    {"css", "*.css *.scss *.sass *.less"},
    {"xml", "*.xml"},
    {"txt", "*.txt"},
}};

struct Options {
    bool ignoreCase = false;
    bool smartCase = false;
    bool fixed = false;
    bool word = false;
    bool line = false;
    bool invert = false;
    bool hidden = false;
    bool noIgnore = false;
    bool binary = false;
    std::vector<std::string> globs;
};

Options options;
std::mutex outputMutex;
std::string_view literal;

using Pattern = std::unique_ptr<pcre2_code, decltype(&pcre2_code_free)>;

void validatePattern(const char* pattern) {
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
}

Pattern compile(const std::string& regex, uint32_t flags) {
    int errcode;
    PCRE2_SIZE erroffset;
    pcre2_compile_context* context = pcre2_compile_context_create(nullptr);
    pcre2_set_newline(context, PCRE2_NEWLINE_ANYCRLF);
    pcre2_code* re = pcre2_compile(reinterpret_cast<PCRE2_SPTR>(regex.data()), regex.size(),
                                   flags, &errcode, &erroffset, context);
    pcre2_compile_context_free(context);

    if (re == nullptr) {
        PCRE2_UCHAR msg[256];
        pcre2_get_error_message(errcode, msg, sizeof(msg));
        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));
    }

    return Pattern(re, pcre2_code_free);
}

bool hasUppercase(std::string_view pattern, bool escapes) {
    for (size_t i = 0; i < pattern.size(); ++i) {
        if (escapes && pattern[i] == '\\') { ++i; continue; }
        if (std::isupper(static_cast<unsigned char>(pattern[i]))) { return true; }
    }
    return false;
}

std::string quote(std::string_view text) {
    std::string quoted = "\\Q";
    for (size_t at; (at = text.find("\\E")) != std::string_view::npos; text.remove_prefix(at + 2)) {
        quoted.append(text.substr(0, at)).append("\\E\\\\E\\Q");
    }
    return quoted.append(text).append("\\E");
}

Pattern compilePattern(std::string_view pattern) {
    if (!options.fixed) { validatePattern(pattern.data()); }

    const bool caseless = options.ignoreCase || (options.smartCase && !hasUppercase(pattern, !options.fixed));
    std::string regex = options.fixed ? quote(pattern) : std::string(pattern);
    if (options.word) { regex = "(?<!\\w)(?:" + regex + ")(?!\\w)"; }
    if (options.line) { regex = "^(?:" + regex + ")$"; }

    const bool plain = options.fixed || pattern.find_first_of("\\^$.|?*+()[]{}") == std::string_view::npos;
    if (plain && !caseless && !options.word && !options.line) { literal = pattern; }

    Pattern re = compile(regex, PCRE2_MULTILINE | PCRE2_USE_OFFSET_LIMIT | (caseless ? PCRE2_CASELESS : 0));
    pcre2_jit_compile(re.get(), PCRE2_JIT_COMPLETE);
    return re;
}

void appendLines(std::string& out, const char* data, size_t from, size_t to) {
    while (from < to) {
        const char* newline = static_cast<const char*>(std::memchr(data + from, '\n', to - from));
        const size_t lineEnd = newline ? static_cast<size_t>(newline - data) : to;
        const size_t trimmed = (lineEnd > from && data[lineEnd - 1] == '\r') ? lineEnd - 1 : lineEnd;
        out.append(data + from, trimmed - from);
        out.push_back('\n');
        from = lineEnd + 1;
    }
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
    size_t printed = start;
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

        if (matched && options.invert) {
            appendLines(out, data, printed, lineStart);
            printed = lineEnd + 1;
        } else if (matched) {
            appendLines(out, data, lineStart, lineEnd);
        }

        pos = lineEnd + 1;
    }

    if (options.invert) { appendLines(out, data, printed, end); }
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

bool isBinary(const char* data, size_t size) {
    return !options.binary && std::memchr(data, '\0', std::min<size_t>(size, 8192)) != nullptr;
}

void grepChunks(HANDLE file, size_t size, size_t chunks, const pcre2_code* expression, std::vector<std::string>& outs) {
    const std::unique_ptr<void, decltype(&CloseHandle)> mapping(
        CreateFileMappingW(file, nullptr, PAGE_READONLY, 0, 0, nullptr), CloseHandle);
    if (!mapping) { return; }

    const View view = mapView(mapping.get());
    if (!view || isBinary(view.get(), size)) { return; }

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

std::string utf8(std::wstring_view text) {
    const int length = static_cast<int>(text.size());
    std::string out(WideCharToMultiByte(CP_UTF8, 0, text.data(), length, nullptr, 0, nullptr, nullptr), '\0');
    WideCharToMultiByte(CP_UTF8, 0, text.data(), length, out.data(), static_cast<int>(out.size()), nullptr, nullptr);
    std::ranges::replace(out, '\\', '/');
    return out;
}

void grepFile(const std::filesystem::path& path, const pcre2_code* expression) {
    HANDLE file = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                              nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);

    if (file == INVALID_HANDLE_VALUE) {
        std::lock_guard<std::mutex> lock(outputMutex);
        std::cerr << utf8(path.native()) << ": Failed to open\n";
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
        if (got == 0 || isBinary(buf.data(), got)) { return; }

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

struct Glob {
    Pattern regex;
    bool negate;
    bool dirOnly;
    bool anchored;
    size_t base;
};

std::string globToRegex(std::string_view glob) {
    std::string regex;
    for (size_t i = 0; i < glob.size(); ++i) {
        const char c = glob[i];
        if (c == '*' && glob.substr(i, 3) == "**/") { regex += "(?:.*/)?"; i += 2; }
        else if (c == '*' && glob.substr(i, 2) == "**") { regex += ".*"; ++i; }
        else if (c == '*') { regex += "[^/]*"; }
        else if (c == '?') { regex += "[^/]"; }
        else if (c == '[' && glob.find(']', i + 2) != std::string_view::npos) {
            const size_t close = glob.find(']', i + 2);
            std::string_view set = glob.substr(i + 1, close - i - 1);
            regex += '[';
            if (set.starts_with('!')) { regex += '^'; set.remove_prefix(1); }
            regex.append(set).push_back(']');
            i = close;
        }
        else {
            const char next = (c == '\\' && i + 1 < glob.size()) ? glob[++i] : c;
            if (!std::isalnum(static_cast<unsigned char>(next)) && next != '/') { regex += '\\'; }
            regex += next;
        }
    }
    return regex;
}

Glob makeGlob(std::string_view text, size_t base) {
    const bool negate = text.starts_with('!');
    if (negate) { text.remove_prefix(1); }
    const bool dirOnly = text.ends_with('/');
    if (dirOnly) { text.remove_suffix(1); }
    const bool anchored = text.find('/') != std::string_view::npos;
    if (text.starts_with('/')) { text.remove_prefix(1); }
    return {compile(globToRegex(text), PCRE2_ANCHORED | PCRE2_ENDANCHORED | PCRE2_CASELESS), negate, dirOnly, anchored, base};
}

bool matches(const Glob& glob, std::string_view path, std::string_view name, bool isDir) {
    thread_local std::unique_ptr<pcre2_match_data, decltype(&pcre2_match_data_free)> matchData(
        pcre2_match_data_create(1, nullptr), pcre2_match_data_free);
    if (glob.dirOnly && !isDir) { return false; }
    const std::string_view subject = glob.anchored ? path.substr(glob.base) : name;
    return pcre2_match(glob.regex.get(), reinterpret_cast<PCRE2_SPTR>(subject.data()), subject.size(),
                       0, 0, matchData.get(), nullptr) >= 0;
}

void loadIgnoreFiles(const std::filesystem::path& dir, size_t base, std::vector<Glob>& rules) {
    for (const char* name : {".gitignore", ".ignore"}) {
        std::ifstream file(dir / name);
        for (std::string line; std::getline(file, line);) {
            while (!line.empty() && std::strchr(" \t\r", line.back())) { line.pop_back(); }
            if (line.empty() || line[0] == '#') { continue; }
            try {
                rules.push_back(makeGlob(line, base));
            }
            catch (const std::exception&) {}
        }
    }
}

bool isIgnored(std::string_view path, std::string_view name, bool isDir,
               const std::vector<Glob>& rules, const std::vector<Glob>& overrides) {
    if (!options.hidden && name.starts_with('.')) { return true; }

    for (auto rule = rules.rbegin(); rule != rules.rend(); ++rule) {
        if (matches(*rule, path, name, isDir)) {
            if (!rule->negate) { return true; }
            break;
        }
    }

    bool included = isDir || std::ranges::all_of(overrides, &Glob::negate);
    for (const Glob& glob : overrides) {
        if (!matches(glob, path, name, isDir)) { continue; }
        if (glob.negate) { return true; }
        included = true;
    }
    return !included;
}

void collectFiles(const std::filesystem::path& dir, const std::vector<Glob>& overrides,
                  std::vector<std::filesystem::path>& files, std::mutex& filesMutex) {
    std::vector<Glob> rules;
    std::vector<size_t> marks;
    if (!options.noIgnore) { loadIgnoreFiles(dir, 0, rules); }
    const size_t rootLength = (dir / L"x").native().size() - 1;

    for (auto it = std::filesystem::recursive_directory_iterator(
            dir,
            std::filesystem::directory_options::skip_permission_denied
        );
        it != std::filesystem::recursive_directory_iterator(); ++it) {

        const auto& entry = *it;
        while (marks.size() > static_cast<size_t>(it.depth())) {
            rules.erase(rules.begin() + static_cast<ptrdiff_t>(marks.back()), rules.end());
            marks.pop_back();
        }

        const bool isDir = entry.is_directory();
        const std::string path = utf8(std::wstring_view(entry.path().native()).substr(rootLength));
        const std::string_view name = std::string_view(path).substr(path.rfind('/') + 1);

        if (isIgnored(path, name, isDir, rules, overrides)) {
            if (isDir) { it.disable_recursion_pending(); }
            continue;
        }

        if (isDir) {
            marks.push_back(rules.size());
            if (!options.noIgnore) { loadIgnoreFiles(entry.path(), path.size() + 1, rules); }
            continue;
        }

        if (entry.is_regular_file()) {
            std::lock_guard<std::mutex> lock(filesMutex);
            files.push_back(entry.path());
        }
    }
}

void addType(std::string_view type, bool exclude) {
    const auto found = std::ranges::find(fileTypes, type, &std::pair<std::string_view, std::string_view>::first);
    if (found == fileTypes.end()) { throw std::runtime_error("Unknown type " + std::string(type)); }

    for (std::string_view globs = found->second; !globs.empty();) {
        const size_t space = std::min(globs.find(' '), globs.size());
        options.globs.push_back((exclude ? "!" : "") + std::string(globs.substr(0, space)));
        globs.remove_prefix(std::min(space + 1, globs.size()));
    }
}

std::vector<std::string_view> parseArgs(int argc, char* argv[]) {
    std::vector<std::string_view> positional;
    bool flagsDone = false;
    int unrestricted = 0;

    for (int i = 1; i < argc; ++i) {
        const std::string_view arg = argv[i];
        if (flagsDone || arg.size() < 2 || arg[0] != '-') { positional.push_back(arg); continue; }
        if (arg == "--") { flagsDone = true; continue; }
        if (arg == "--hidden") { options.hidden = true; continue; }
        if (arg.starts_with("--")) { throw std::runtime_error("Unknown flag " + std::string(arg)); }

        for (size_t j = 1; j < arg.size(); ++j) {
            const char flag = arg[j];
            if (std::strchr("gtT", flag)) {
                std::string_view value = arg.substr(j + 1);
                if (value.empty()) {
                    if (++i == argc) { throw std::runtime_error(std::string("Missing value for -") + flag); }
                    value = argv[i];
                }
                if (flag == 'g') { options.globs.emplace_back(value); }
                else { addType(value, flag == 'T'); }
                break;
            }
            switch (flag) {
                case 'i': options.ignoreCase = true; break;
                case 'S': options.smartCase = true; break;
                case 'F': options.fixed = true; break;
                case 'w': options.word = true; break;
                case 'x': options.line = true; break;
                case 'v': options.invert = true; break;
                case 'a': options.binary = true; break;
                case 'u': ++unrestricted; break;
                default: throw std::runtime_error(std::string("Unknown flag -") + flag);
            }
        }
    }

    options.noIgnore |= unrestricted >= 1;
    options.hidden |= unrestricted >= 2;
    options.binary |= unrestricted >= 3;
    return positional;
}

int main(int argc, char* argv[]) {
    // in text mode, the C runtime converts every \n to \r\n byte by byte.
    // That happens while the output mutex is held, so all 16 threads queue up behind it
    _setmode(_fileno(stdout), _O_BINARY);

    std::vector<std::string_view> positional;
    Pattern expression(nullptr, pcre2_code_free);
    std::vector<Glob> overrides;
    try {
        positional = parseArgs(argc, argv);
        if (positional.size() != 2) { throw std::runtime_error(std::string(usage)); }
        expression = compilePattern(positional[1]);
        for (const std::string& glob : options.globs) { overrides.push_back(makeGlob(glob, 0)); }
    }
    catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 2;
    }

    std::filesystem::path dir = std::filesystem::current_path();
    dir /= positional[0];

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
                    std::cerr << utf8(path.native()) << ": " << e.what() << "\n";
                }
            }
        });
    }

    collectFiles(dir, overrides, files, filesMutex);
    { std::lock_guard<std::mutex> lock(filesMutex); walked = true; }

    for (auto& thread : threads) {
        thread.join();
    }

    return 0;
}
