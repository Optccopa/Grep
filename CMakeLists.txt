cmake_minimum_required(VERSION 3.21)
set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)
project(tooling LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)

find_package(pcre2 CONFIG REQUIRED)

file(GLOB tools CONFIGURE_DEPENDS src/*.cpp)
foreach(t ${tools})
    cmake_path(GET t STEM name)
    add_executable(${name} ${t})
    target_link_libraries(${name} PRIVATE PCRE2::8BIT)
endforeach()