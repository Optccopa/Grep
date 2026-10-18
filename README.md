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
