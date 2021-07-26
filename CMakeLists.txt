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

#set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")
#set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3")

#if(CMAKE_BUILD_TYPE)
#  add_compile_options("-O3")
#endif()

if (WIN32)
  add_definitions(-D_DISABLE_EXTENDED_ALIGNED_STORAGE)
endif()

# OPTIONS
set (CMAKE_CXX_STANDARD 14)

if(EXISTS ${PROJECT_SOURCE_DIR}/lib/pybind11/CMakeLists.txt)
    add_subdirectory(${PROJECT_SOURCE_DIR}/lib/pybind11)
else()
    find_package(pybind11 REQUIRED)
endif()
  

# FIND DEPENDENCIES

if(EXISTS ${PROJECT_SOURCE_DIR}/lib/fmt/CMakeLists.txt)
    add_subdirectory(lib/fmt)
else()
    find_package(fmt)
endif()

add_subdirectory(src xfoil)

MESSAGE(STATUS "installing to ${python_libs}")
