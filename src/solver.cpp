#include "solver.hpp"


bool Solver::load(std::vector<std::pair<double, double>> vectors) {
    std::stringstream stream;

    this->solver.setCancel(false);
    if(!this->solver.initXFoilGeometry(vectors)) {
        return false;
    }

    
    if(!this->solver.initXFoilAnalysis(this->reynolds, 0, this->mach, this->ncrit, this->xtr_top, this->xtr_bottom,
                                          this->re_type, this->mach_type, this->viscous, stream)){
        return false;
    }
    /*
    */

    return true;

};

Result Solver::run_aoa(double aoa) {
    this->solver.setAlpha(aoa);
    this->solver.lalfa = true;

    this->solver.lwake = false;
    this->solver.lvconv = false;


    this->solver.setQInf(1.0);
    auto str = fmt::format("Alpha = {:.3f}°", aoa*180/PI);
    //traceLog(str);

    // here we go !

    this->solver.setBLInitialized(false);
    this->solver.lipan = false;

    return this->solve();
}

Result Solver::run_cl(double cl) {
    this->solver.lalfa = false;
    this->solver.setAlpha(0.0);
    this->solver.setQInf(1.0);
    this->solver.setClSpec(cl);
    auto str = fmt::format("Cl = {:.3f}", this->solver.ClSpec());
    //traceLog(str);
    if(!this->solver.speccl())
    {
        str = std::string("Invalid Analysis Settings\nCpCalc: local speed too large\n Compressibility corrections invalid ");
        //traceLog(str);
        //m_bErrors = true;
        // todo: throw
    }

    return this->solve();
}

Result Solver::solve() {

    if (!this->solver.specal())
    {
        auto str = std::string("Invalid Analysis Settings\nCpCalc: local speed too large\n Compressibility corrections invalid ");
        //traceLog(str);
        //m_bErrors = true;
        //return false;
        Result result;
        result.converged = false;
        return result;
    }
    

    this->solver.lwake = false;
    this->solver.lvconv = false;

    int m_Iterations = 0;

    while(m_Iterations <= 0) {
        m_Iterations += this->iterate();
    }

    std::string str;

    if(this->solver.lvconv) {
        str = fmt::format("   ...converged after {} iterations\n", m_Iterations);

        return this->getResult();
        //traceLog(str);
    } else {
        str = fmt::format("   ...unconverged after {} iterations\n", m_Iterations);
        throw std::runtime_error(str);
    }

    /*
    if(XFoil::fullReport())
    {
        m_XFoilStream.flush();
        traceLog(m_XFoilLog);
        m_XFoilLog.clear();

    if(m_x0) m_x0->clear();
    if(m_x1) m_x1->clear();
    if(m_y0) m_y0->clear();
    if(m_y1) m_y1->clear();
    }*/

}

int Solver::iterate() {
    
    if(!this->solver.viscal())
    {
        this->solver.lvconv = false;
        this->solver.write("CpCalc: local speed too large\n Compressibility corrections invalid");
        return 0;
    }

    using veclist = std::vector<std::pair<double, double>>;

    veclist convergence_1, convergence_2;

    unsigned int i = 0;

    while(i<this->max_iterations && !this->solver.lvconv) {
        if(this->solver.ViscousIter()) {
            convergence_1.push_back({double(i), this->solver.rmsbl});
            convergence_2.push_back({double(i), this->solver.rmxbl});
            
            i++;
        } else {
            i = this->max_iterations;
        }
    }

    if(!this->solver.ViscalEnd())
    {
        this->solver.lvconv = false;//point is unconverged

        this->solver.setBLInitialized(false);
        this->solver.lipan = false;
        
        throw std::runtime_error("unconverged");
    }


    if(i>=this->max_iterations && !this->solver.lvconv) {
        if(this->initialize_bl_auto)
        {
            this->solver.setBLInitialized(false);
            this->solver.lipan = false;
        }
        this->solver.fcpmin();// Is it of any use ?
    }
    if(!this->solver.lvconv) {
        this->solver.fcpmin();// Is it of any use ?
        throw std::runtime_error("unconverged");
    } else {
        //converged at last
        this->solver.fcpmin();// Is it of any use ?
    }


    return i;
}

std::vector<Result> Solver::run_aoa(std::vector<double> aoa) {
    std::string str;

    std::vector<Result> result;

    this->solver.setBLInitialized(false);
    this->solver.lipan = false;

    for (auto alpha: aoa) {
        this->solver.setAlpha(alpha);
        this->solver.lalfa = true;
        this->solver.setQInf(1.0);

        try {
            result.push_back(this->solve());
        } catch(std::runtime_error) {
            Result unconverged_result;
            unconverged_result.aoa = alpha*180.0/PI;
            unconverged_result.converged = false;
            result.push_back(unconverged_result);
        }
    }

    return result;

/*
    double SpMin=0, SpMax=0, SpInc=0;




        if(true) // initBL
        {
            this->solver.setBLInitialized(false);
            this->solver.lipan = false;
        }

        for (auto alpha: aoa) {

            this->solver.setAlpha(alpha);
            this->solver.lalfa = true;
            this->solver.setQInf(1.0);

            // here we go !
            if (!this->solver.specal())
            {
                str = std::string("Invalid Analysis Settings\nCpCalc: local speed too large\n Compressibility corrections invalid ");
                throw std::runtime_error(str);
            }
            

            this->solver.lwake = false;
            this->solver.lvconv = false;


            while(!iterate()){}

            if(this->solver.lvconv)
            {
                str = QString(QObject::tr("   ...converged after %1 iterations\n")).arg(m_Iterations);
                traceLog(str);
                if(m_pParent)
                {
                    OpPoint *pOpPoint = new OpPoint;
                    addXFoilData(pOpPoint, &this->solver, m_pFoil);
                    qApp->postEvent(m_pParent, new XFoilOppEvent(m_pFoil, m_pPolar, pOpPoint));
                }
            }
            else
            {
                str = QString(QObject::tr("   ...unconverged after %1 iterations\n")).arg(m_Iterations);
                traceLog(str);
                m_bErrors = true;
            }

            if(XFoil::fullReport())
            {
                m_XFoilStream.flush();
                traceLog(m_XFoilLog);
                m_XFoilLog.clear();
            }

            if(m_x0) m_x0->clear();
            if(m_x1) m_x1->clear();
            if(m_y0) m_y0->clear();
            if(m_y1) m_y1->clear();

        }// end Alpha or Cl loop
    }
    //        strong+="\n";
    return true;
*/
}

Result Solver::getResult() { //Foil *pFoil
    auto pXFoil = &(this->solver);

    int i=0, j=0, ibl=0, is=0;

    Result result;

    result.aoa          = pXFoil->alfa*180.0/PI;
    //result.n            = pXFoil->n;
    result.cd           = pXFoil->cd;
    result.cdp          = pXFoil->cdp;
    result.cl           = pXFoil->cl;
    //result.m_XCP        = pXFoil->xcp;
    result.cm           = pXFoil->cm;
    result.reynolds     = pXFoil->reinf;
    result.converged    = true;
    //result.m_Mach       = pXFoil->minf;
    //result.ACrit        = pXFoil->acrit;

    //result.m_bTEFlap    = pFoil->m_bTEFlap;
    //result.m_bLEFlap    = pFoil->m_bLEFlap;

    //result.Cpmn   = pXFoil->cpmn;


    /*
    for (int k=0; k<pXFoil->n; k++) {
        //        x[k]   = m_pXFoil->x[k+1];
        //        y[k]   = m_pXFoil->y[k+1];
        //        s[k]   = m_pXFoil->s[k+1];
        result.Cpi[k] = pXFoil->cpi[k+1];
        result.Qi[k]  = pXFoil->qgamm[k+1];
    }

    */
    if(pXFoil->lvisc && pXFoil->lvconv) {
        result.xtr_top =pXFoil->xoctr[1];
        result.xtr_bottom =pXFoil->xoctr[2];
        result.is_viscous = true;

        //result.m_bBL = true;
        /*
        for (int k=0; k<pXFoil->n; k++) {
            result.Cpv[k] = pXFoil->cpv[k+1];
            result.Qv[k] = pXFoil->qvis[k+1];
        }*/
    } else {
        result.is_viscous = false;
    }

    /*

    if(result.m_bTEFlap || result.m_bLEFlap) {
        result.setHingeMoments(pFoil);
        result.m_TEHMom = pXFoil->hmom;
        result.XForce   = pXFoil->hfx;
        result.YForce   = pXFoil->hfy;
    }

    if(!pXFoil->lvisc || !pXFoil->lvconv) {
        return;
    }

    //---- add boundary layer on both sides of airfoil
    result.blx.nd1=0;
    result.blx.nd2=0;
    result.blx.nd3=0;

    for (is=1; is<=2; is++)
    {
        for (ibl=2; ibl<=pXFoil->iblte[is];ibl++)
        {
            i = pXFoil->ipan[ibl][is];
            result.blx.xd1[i] = pXFoil->x[i] + pXFoil->nx[i]*pXFoil->dstr[ibl][is];
            result.blx.yd1[i] = pXFoil->y[i] + pXFoil->ny[i]*pXFoil->dstr[ibl][is];
            result.blx.nd1++;
        }
    }

    //---- set upper and lower wake dstar fractions based on first wake point
    is=2;
    double dstrte = pXFoil->dstr[pXFoil->iblte[is]+1][is];
    double dsf1, dsf2;
    if(dstrte!=0.0) // d* at TE
    {
        dsf1 = (pXFoil->dstr[pXFoil->iblte[1]][1] + 0.5*pXFoil->ante) / dstrte;
        dsf2 = (pXFoil->dstr[pXFoil->iblte[2]][2] + 0.5*pXFoil->ante) / dstrte;
    }
    else
    {
        dsf1 = 0.5;
        dsf2 = 0.5;
    }

    //---- plot upper wake displacement surface
    ibl = pXFoil->iblte[1];
    i = pXFoil->ipan[ibl][1];
    result.blx.xd2[0] = pXFoil->x[i] + pXFoil->nx[i]*pXFoil->dstr[ibl][1];
    result.blx.yd2[0] = pXFoil->y[i] + pXFoil->ny[i]*pXFoil->dstr[ibl][1];
    result.blx.nd2++;

    j= pXFoil->ipan[pXFoil->iblte[is]+1][is]  -1;
    for (ibl=pXFoil->iblte[is]+1; ibl<=pXFoil->nbl[is]; ibl++)
    {
        i = pXFoil->ipan[ibl][is];
        result.blx.xd2[i-j] = pXFoil->x[i] - pXFoil->nx[i]*pXFoil->dstr[ibl][is]*dsf1;
        result.blx.yd2[i-j] = pXFoil->y[i] - pXFoil->ny[i]*pXFoil->dstr[ibl][is]*dsf1;
        result.blx.nd2++;
    }

    //---- plot lower wake displacement surface
    ibl = pXFoil->iblte[2];
    i = pXFoil->ipan[ibl][2];
    result.blx.xd3[0] = pXFoil->x[i] + pXFoil->nx[i]*pXFoil->dstr[ibl][2];
    result.blx.yd3[0] = pXFoil->y[i] + pXFoil->ny[i]*pXFoil->dstr[ibl][2];
    result.blx.nd3++;

    j = pXFoil->ipan[pXFoil->iblte[is]+1][is]  -1;
    for (ibl=pXFoil->iblte[is]+1; ibl<=pXFoil->nbl[is]; ibl++)
    {
        i = pXFoil->ipan[ibl][is];
        result.blx.xd3[i-j] = pXFoil->x[i] + pXFoil->nx[i]*pXFoil->dstr[ibl][is]*dsf2;
        result.blx.yd3[i-j] = pXFoil->y[i] + pXFoil->ny[i]*pXFoil->dstr[ibl][is]*dsf2;
        result.blx.nd3++;
    }

    result.blx.tklam = pXFoil->tklam;
    result.blx.qinf = pXFoil->qinf;

    memcpy(result.blx.thet, pXFoil->thet, IVX * ISX * sizeof(double));
    memcpy(result.blx.tau,  pXFoil->tau,  IVX * ISX * sizeof(double));
    memcpy(result.blx.ctau, pXFoil->ctau, IVX * ISX * sizeof(double));
    memcpy(result.blx.ctq,  pXFoil->ctq,  IVX * ISX * sizeof(double));
    memcpy(result.blx.dis,  pXFoil->dis,  IVX * ISX * sizeof(double));
    memcpy(result.blx.uedg, pXFoil->uedg, IVX * ISX * sizeof(double));
    memcpy(result.blx.dstr, pXFoil->dstr, IVX * ISX * sizeof(double));
    memcpy(result.blx.itran, pXFoil->itran, 3 * sizeof(int));

    pXFoil->createXBL();
    pXFoil->fillHk();
    pXFoil->fillRTheta();
    memcpy(result.blx.xbl, pXFoil->xbl, IVX * ISX * sizeof(double));
    memcpy(result.blx.Hk, pXFoil->Hk, IVX * ISX * sizeof(double));
    memcpy(result.blx.RTheta, pXFoil->RTheta, IVX * ISX * sizeof(double));
    result.blx.nside1 = pXFoil->m_nSide1;
    result.blx.nside2 = pXFoil->m_nSide2;*/

    return result;
}
