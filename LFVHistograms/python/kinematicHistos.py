import ROOT as r

class kinematicHistos:
    def __init__(self, physObj="mu", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        prefix = "h_data"
        self.mcType = mcType
        if self.mcType is not None:
            prefix = "h_%s"%mcType
        
        self.charge = r.TH1F("%s_%s_charge_%s"%(prefix,physObj,selLevel),"%s charge - %s"%(physObj, selLevel), 5,-2.5,2.5)
        self.energy = r.TH1F("%s_%s_energy_%s"%(prefix,physObj,selLevel),"%s E - %s"%(physObj, selLevel), 300,-0.5,2999.5)
        self.eta = r.TH1F("%s_%s_eta_%s"%(prefix,physObj,selLevel),"%s eta - %s"%(physObj, selLevel), 49,-2.45,2.45)
        self.mass = r.TH1F("%s_%s_mass_%s"%(prefix,physObj,selLevel),"%s mass - %s"%(physObj, selLevel), 700,-0.5,6999.5)
        self.multi = r.TH1F("%s_%s_multi_%s"%(prefix,physObj,selLevel),"%s multiplicity - %s"%(physObj, selLevel), 30,-0.5,29.5)
        self.pt = r.TH1F("%s_%s_pt_%s"%(prefix,physObj,selLevel),"%s p_{T} - %s"%(physObj, selLevel), 300,-0.5,2999.5)
        self.pz = r.TH1F("%s_%s_pz_%s"%(prefix,physObj,selLevel),"%s p_{Z} - %s"%(physObj, selLevel), 400,-2000.5,1999.5)
        if self.mcType == "reco":
            self.dR = r.TH1F("%s_%s_dR_%s"%(prefix,physObj,selLevel),
                    "%s #DeltaR#left(reco,gen#right) - %s"%(physObj, selLevel),
                    102,-0.05,5.05)
            self.dRMatched = r.TH1F("%s_%s_dRMatched_%s"%(prefix,physObj,selLevel),
                    "%s #DeltaR#left(reco,gen#right) After Matching - %s"%(physObj, selLevel),
                    102,-0.05,5.05)
            self.ptRes = r.TH1F("%s_%s_ptRes_%s"%(prefix,physObj,selLevel),
                    "%s #left(#left(p_{T}^{reco} - p_{T}^{gen}#right) / p_{T}^{gen}#right) - %s"%(physObj, selLevel), 
                    100,-2.5,2.5) #(reco - gen) / gen
            pass

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        directory.cd()

        self.charge.Write()
        self.energy.Write()
        self.eta.Write()
        self.mass.Write()
        self.multi.Write()
        self.pt.Write()
        if self.mcType == "reco":
            self.dR.Write()
            self.dRMatched.Write()
            self.ptRes.Write()
            pass
        self.pz.Write()

        return
