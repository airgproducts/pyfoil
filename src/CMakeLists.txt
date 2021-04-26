# Build the c++ shared library
set(CMAKE_SOURCE_DIR ${CMAKE_SOURCE_DIR}/src)
set(HEADER_FILES 
		format.hpp
		xfoil_params.h
		xfoil.h
		)

set(CPP_FILES xfoil.cpp)

#add_library(xfoil STATIC ${CPP_FILES} ${HEADER_FILES})
#install(TARGETS pm DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)


pybind11_add_module(xfoil pybind.cpp ${CPP_FILES} ${HEADER_FILES})
