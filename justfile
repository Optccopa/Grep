configure:
    @clear
    powershell -Command "if (Test-Path 'build') { Remove-Item -Path 'build' -Recurse -Force }"
    cmake -B build

build config="Release":
    @clear
    cmake --build build --config {{config}}

run config="Release":
    @clear
    cmake --build build --config {{config}}
    powershell -Command "./build/{{config}}/grep.exe . conf"

test:
    @powershell -Command "py ./tests/test_grep.py -q"
