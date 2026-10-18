# Grep

A simple grep tool written in C++20, ~3x faster than GNU grep and matches ripgrep on small folders.

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
| Small | literal `constexpr` | **16 ms** | 23 ms | 110 ms |
| Small | regex `_[A-Z]+_[A-Z]+[(]` | **18 ms** | 25 ms | 158 ms |
| Small | no match `zqxjvk` | **16 ms** | 23 ms | 111 ms |
| Large | literal `HRESULT` | 183 ms | **123 ms** | 1587 ms |
| Large | regex `_[A-Z]+_[A-Z]+[(]` | 172 ms | **138 ms** | 2101 ms |
| Large | no match `zqxjvk` | 167 ms | **118 ms** | 1782 ms |
