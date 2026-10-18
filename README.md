# Grep

A simple grep tool written in C++20, ~3x faster than GNU grep, ~1.5x faster than ripgrep in most cases.

## Install and Run
```bash
git clone https://github.com/Optccopa/Grep
cd Grep
cmake -B build
cmake --build build --config Release
./build/Release/grep.exe . "a"
```

## Benchmarks (Windows 11, Ryzen 7 5700G (8C/16T))

Median of 20 warm-cache runs. All greps skip binary files. ([Bench Script](bench.py))

- **Small:** MSVC STL headers, 353 files, 15 MB
- **Large:** Windows SDK 10.0.26100.0 headers, 4,771 files, 345 MB

| Corpus | Search | this grep | ripgrep | GNU grep 3.0 |
|---|---|---:|---:|---:|
| Small | literal `constexpr` | **12 ms** | 24 ms | 69 ms |
| Small | regex `_[A-Z]+_[A-Z]+[(]` | **11 ms** | 23 ms | 100 ms |
| Small | no match `zqxjvk` | **11 ms** | 22 ms | 78 ms |
| Large | literal `HRESULT` | 74 ms | **72 ms** | 774 ms |
| Large | regex `_[A-Z]+_[A-Z]+[(]` | **66 ms** | 81 ms | 1320 ms |
| Large | no match `zqxjvk` | **58 ms** | 63 ms | 931 ms |
