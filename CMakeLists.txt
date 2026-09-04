cmake_minimum_required(VERSION 3.21)
project(grep LANGUAGES CXX)

find_package(pcre2 CONFIG REQUIRED)

add_executable(grep src/grep.cpp)
target_compile_features(grep PRIVATE cxx_std_20)
target_link_libraries(grep PRIVATE PCRE2::8BIT)