# Grep

A simple grep tool written in C++20, ~3x faster than GNU grep, ~1.5x faster than ripgrep in most cases.

## Install and Run
### Prerequisites
- Visual Studio 2022 or newer with the **Desktop development with C++ workload**
- CMake 3.28+
- git
### Optional Prerequisites
- [just](https://github.com/casey/just) - Way nicer commands (below)
- Python 3.10+
- For benchmarks:
  - [ripgrep](https://github.com/BurntSushi/ripgrep) on your `PATH`.
  - The two header folders the benchmarks search, at the paths set in `scripts/bench.py`: the MSVC 14.51 STL headers and the Windows SDK 10.0.26100.0 headers. If your versions differ, edit `SMALL` and `LARGE`.
  - Git for Windows, the bundled grep 3.0 is used.

### Clone source
```bash
git clone https://github.com/Optccopa/Grep
cd Grep
```

### With just (reccomended, optional install)
```bash
just configure # Configure the build folder
just build # Build the exe
just test # Run tests
just bench # Run benchmarks against rg and GNU grep
```

### With CMake
```bash
cmake -B build # Configure the build folder
cmake --build build --config Release # Build the exe
py ./tests/test_grep.py -q # Run tests
py ./scripts/bench.py --fast # Run benchmarks against rg and GNU grep
```

## Benchmarks (Windows 11, Ryzen 7 5700G (8C/16T))

Median of 20 warm-cache runs. All greps skip binary files.

Each value is a mean over 10 flag sets of the median of 10 runs.

Flag sets: none, -i, -S, -F, -w, -x, -v, [-i, -w], [-i, -F], [-i, -v]
- **Small:** MSVC STL headers, 353 files, 15 MB
- **Large:** Windows SDK 10.0.26100.0 headers, 4,771 files, 345 MB

| Corpus | Search | this grep | ripgrep | GNU grep 3.0 |
|---|---|---:|---:|---:|
| Small | literal `constexpr` | **13 ms** | 26 ms | 148 ms |
| Small | regex `_[A-Z]+_[A-Z]+[(]` | **14 ms** | 27 ms | 150 ms |
| Small | no match `zqxjvk` | **13 ms** | 25 ms | 149 ms |
| Large | literal `HRESULT` | **114 ms** | 135 ms | 1633 ms |
| Large | regex `_[A-Z]+_[A-Z]+[(]` | **118 ms** | 154 ms | 1872 ms |
| Large | no match `zqxjvk` | **111 ms** | 129 ms | 1747 ms |

## Usage
```text
usage: grep [flags] <path> <pattern>
  -i         ignore case
  -S         smart case: ignore case unless the pattern has an uppercase letter
  -F         treat the pattern as a fixed string
  -w         match whole words only
  -x         match whole lines only
  -v         print lines that do not match
  -a         search binary files as text
  -g GLOB    only search files matching GLOB, !GLOB excludes (repeatable)
  -t TYPE    only search files of TYPE, -T TYPE excludes them (repeatable)
  --hidden   search hidden files and folders
  -u         don't respect .gitignore/.ignore, -uu also --hidden, -uuu also -a
  --         end of flags
```
