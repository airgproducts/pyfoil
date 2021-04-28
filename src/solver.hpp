#include "xfoil.h"


struct Result {
    double aoa;
    
    double cl = 0;
    double cd = 0;
    double cdp = 0;
    double cm = 0;

    double xtr_top = 0;
    double xtr_bottom = 0;
    double reynolds;

    bool is_viscous;
    bool converged = false;
};


class Solver {
    public:
        Solver() : solver() {};

        bool load(std::vector<std::pair<double, double>> coordinates);

        Result run_aoa(double aoa);
        Result run_cl(double cl);

        std::vector<Result> run_aoa(std::vector<double> aoa);
        std::vector<Result> run_cl(std::vector<double> aoa);

        bool viscous = true;

        double ncrit = 4;
        double xtr_top = 0.5;
        double xtr_bottom = 0.5;

        int re_type = 1;
        int mach_type = 1;

        double reynolds = 2e6;
        double mach = 0.;


        unsigned int max_iterations = 200;

        bool initialize_bl_auto = true;

    private:
        Result solve();
        Result getResult();
        int iterate();

        std::vector<std::tuple<double, double>> coordinates;

        XFoil solver;
    
};