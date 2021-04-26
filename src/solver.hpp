#include "xfoil.h"


struct Result {
    double cl;
    double cd;
    double cm;



};


class Solver {
    public:
        Solver();

        void load(std::vector<std::tuple<double, double>> coordinates);

        Result run_aoa(double aoa);
        Result run_cl(double cl);

        std::vector<Result> run_aoa(std::vector<double> aoa);
        std::vector<Result> run_cl(std::vector<double> aoa);

        double ncrit;

    private:
        std::vector<std::tuple<double, double>> coordinates;
    
};