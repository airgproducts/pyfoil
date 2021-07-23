#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "solver.hpp"
#include "version.hpp"

namespace py=pybind11;

PYBIND11_MODULE(xfoil, m) {
    m.doc() = "xfoil for python";

    py::class_<Result>(m, "Result", py::dynamic_attr())
        .def_readonly("aoa", &Result::aoa)
        .def_readonly("cl", &Result::cl)
        .def_readonly("cd", &Result::cd)
        .def_readonly("cdp", &Result::cdp)
        .def_readonly("cm", &Result::cm)
        .def_readonly("xtr_top", &Result::xtr_top)
        .def_readonly("xtr_bottom", &Result::xtr_bottom)
        .def_readonly("reynolds", &Result::reynolds)
        .def_readonly("converged", &Result::converged)
        .def("__repr__", [](const Result& result) {
            std::stringstream out;

            out << "cl\t" << result.cl << "\n";
            out << "cd\t" << result.cd << "\n";
            out << "cdp\t" << result.cdp << "\n";
            out << "cm\t" << result.cm << "\n";
            out << "xtr_top\t" << result.xtr_top << "\n";
            out << "xtr_bottom\t" << result.xtr_bottom << "\n";
            out << "reynolds\t" << result.reynolds << "\n";
            out << "converged\t" << result.converged;


            return out.str();
        });

    py::class_<Solver>(m, "Solver")
        .def(py::init<>())
        .def("load", &Solver::load)
        .def("run_aoa", py::overload_cast<double>(&Solver::run_aoa))
        .def("run_aoa", py::overload_cast<std::vector<double>>(&Solver::run_aoa))

        .def("set_debug", [](Solver& solver, bool debug) {
            solver.set_debug(debug);
        })

        .def_readwrite("viscous", &Solver::viscous)
        .def_readwrite("xtr_top", &Solver::xtr_top)
        .def_readwrite("xtr_bottom", &Solver::xtr_bottom)
        .def_readwrite("ncrit", &Solver::ncrit);

    m.attr("__version__") = py::str(version);
}