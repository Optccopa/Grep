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

constexpr std::array<std::string_view, 6> ignoredFolders{
    "node_modules",
    "build",
    "out",
    "dist",
    "obj",
    "__pycache__"
};

using Pattern = std::unique_ptr<pcre2_code, decltype(&pcre2_code_free)>;

Pattern compileRegexPattern(char* pattern) {
    int errcode;
    PCRE2_SIZE erroffset;
    pcre2_code* re = pcre2_compile(reinterpret_cast<PCRE2_SPTR>(pattern),
                                   PCRE2_ZERO_TERMINATED, 0, &errcode, &erroffset, nullptr);

    if (re == nullptr) {
        PCRE2_UCHAR msg[256];
        pcre2_get_error_message(errcode, msg, sizeof(msg));
        throw std::runtime_error("Bad pattern: " + std::string(reinterpret_cast<char*>(msg)));
    }

    pcre2_jit_compile(re, PCRE2_JIT_COMPLETE);

    return Pattern(re, pcre2_code_free);
}

void grepFile(const std::filesystem::path& path, const pcre2_code* expression) {
    std::ifstream file(path);

    if (!file.is_open()) {
        std::cerr << path.string() << ": Failed to open\n";
        return;
    }

    char probe[8192];

    file.read(probe, sizeof(probe));
    
    const std::streamsize got = file.gcount();

    if (std::memchr(probe, '\0', static_cast<size_t>(got)) != nullptr) { return; }

    file.clear();
    file.seekg(0);

    std::unique_ptr<pcre2_match_data, decltype(&pcre2_match_data_free)> matchData(
        pcre2_match_data_create_from_pattern(expression, nullptr), pcre2_match_data_free);

    std::vector<std::string> matches;

    std::string line;
    while(std::getline(file, line)) {
        int rc = pcre2_match(expression, reinterpret_cast<PCRE2_SPTR>(line.data()),
                             line.size(), 0, 0, matchData.get(), nullptr);

        if (rc >= 0) {
            std::cout << line << "\n";
        }
        else if (rc != PCRE2_ERROR_NOMATCH) {
            throw std::runtime_error("Match error: " + std::to_string(rc));
        }
    }
    return;
}

int main(int argc, char* argv[]) {
    std::filesystem::path dir = std::filesystem::current_path();
    dir /= argv[1];

    Pattern expression = compileRegexPattern(argv[2]);

    if (std::filesystem::is_regular_file(dir)) {
        grepFile(dir, expression.get());
        return 0;
    }

    for (auto it = std::filesystem::recursive_directory_iterator(dir, std::filesystem::directory_options::skip_permission_denied);
        it != std::filesystem::recursive_directory_iterator(); ++it) {

        const auto& entry = *it;

        if (entry.is_directory()) {
            const std::string fileName = entry.path().filename().string();
            if (fileName.starts_with(".") || std::ranges::find(ignoredFolders, fileName) != ignoredFolders.end()) {
                it.disable_recursion_pending();
                continue;
            }
        }

        if (entry.is_regular_file()) {
            grepFile(entry, expression.get());
        }
    }

    return 0;
}