cmake_minimum_required(VERSION 3.28)
project(grep LANGUAGES CXX)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

include(FetchContent)

set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(PCRE2_BUILD_PCRE2_8 ON CACHE BOOL "" FORCE)
set(PCRE2_SUPPORT_JIT ON CACHE BOOL "" FORCE)
set(PCRE2_BUILD_PCRE2GREP OFF CACHE BOOL "" FORCE)
set(PCRE2_BUILD_TESTS OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
    pcre2
    GIT_REPOSITORY https://github.com/PCRE2Project/pcre2.git
    GIT_TAG pcre2-10.47
    GIT_SHALLOW TRUE
    GIT_SUBMODULES_RECURSIVE TRUE
)
FetchContent_MakeAvailable(pcre2)

add_executable(grep src/main.cpp)
target_compile_features(grep PRIVATE cxx_std_20)
target_link_libraries(grep PRIVATE pcre2-8)
