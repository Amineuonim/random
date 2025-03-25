cmake_minimum_required(VERSION 3.10)
project(OpenGLApp)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)

include_directories(include/glad/include)

add_executable(OpenGLApp src/main.cpp include/glad/src/glad.c)
target_link_libraries(OpenGLApp glfw OpenGL::GL dl)
