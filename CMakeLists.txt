cmake_minimum_required(VERSION 3.0)
project(xfoil)
MESSAGE(STATUS "python version set: ${py}")

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

OPTION(BUILD_PYTHON_BINDINGS "build the python bindings" ON)
OPTION(BUILD_WITH_MPI "switch multithreading support" ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")

if (WIN32)
  add_definitions(-D_DISABLE_EXTENDED_ALIGNED_STORAGE)
endif()

# OPTIONS
set (CMAKE_CXX_STANDARD 11)
OPTION(BUILD_PYTHON_BINDINGS "create python bindings" ON)

if (BUILD_PYTHON_BINDINGS)
  ## PYTHON
  set(Python_ADDITIONAL_VERSIONS ${py})
  find_package(PythonInterp ${py} REQUIRED)
  find_package(PythonLibs ${py} REQUIRED)
  find_package(pybind11 2.0 REQUIRED)
endif()

# FIND DEPENDENCIES

add_subdirectory(lib/fmt)
add_subdirectory(src)

MESSAGE(STATUS "installing to ${python_libs}")
