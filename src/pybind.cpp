#include <pybind11/pybind11.h>

#include "solver.hpp"
#include "version.hpp"

namespace py=pybind11;

PYBIND11_MODULE(xfoil, m) {
    m.doc() = "xfoil for python";

    py::class_<Result>(m, "Result")
        .def_readonly("cl", &Result::cl)
        .def_readonly("cd", &Result::cd)
        .def_readonly("cm", &Result::cm);

    m.attr("__version__") = py::str(version);
}