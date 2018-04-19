import ROOT as r

class identificationHistos:
    def __init__(self, listIdLabels=None, physObj="mu", selLevel="all", mcType=None):
        """
        listIdLabels - list of strings specifying ID labels
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType
            pass

        # Make the label histogram and set the labels
        self.idLabel = None
        if listIdLabels is not None:
            self.idLabel = r.TH1F("%s_%s_idLabel_%s"%(prefix,physObj,selLevel),
                                  "%s Id Label - %s"%(physObj, selLevel), 
                                  len(listIdLabels),0.5,len(listIdLabels)+0.5
                                  )
            for binX,label in enumerate(listIdLabels):
                self.idLabel.GetXaxis().SetBinLabel(binX+1,label)
                pass

            self.idLabel_vs_pt = r.TH2F("%s_%s_idLabel_vs_pt_%s"%(prefix,physObj,selLevel),
                                           "%s idLabel vs. p_{T} - %s"%(physObj, selLevel),
                                           300,-0.5,2999.5,
                                           len(listIdLabels),0.5,len(listIdLabels)+0.5)
            self.idLabel_vs_ptRes = r.TH2F("%s_%s_idLabel_vs_ptRes_%s"%(prefix,physObj,selLevel),
                                           "%s idLabel vs. #left(#left(p_{T}^{reco} - p_{T}^{gen}#right) / p_{T}^{gen}#right) - %s"%(physObj, selLevel),
                                           100,-2.5,2.5, #(reco - gen) / gen
                                           len(listIdLabels),0.5,len(listIdLabels)+0.5)
            
            # Set Id Labels for certain histograms
            for binY,idLabel in enumerate(tauIdLabels):
                self.idLabel_vs_pt.GetYaxis().SetBinLabel(binY+1,idLabel)
                self.idLabel_vs_ptRes.GetYaxis().SetBinLabel(binY+1,idLabel)
                pass
            pass

        # Make impact parameter histograms
        self.dxy = r.TH1F("%s_%s_dxy_%s"%(prefix,physObj,selLevel),
                          "%s d_{xy} - %s"%(physObj, selLevel),
                          110,-5.5,5.5)
        self.dz = r.TH1F("%s_%s_dz_%s"%(prefix,physObj,selLevel),
                          "%s d_{z} - %s"%(physObj, selLevel),
                          210,-10.5,10.5)

        # Make track fit histograms (not always relevant)
        self.normChi2 = r.TH1F("%s_%s_normChi2_%s"%(prefix,physObj,selLevel),
                               "%s #chi^{2}/NDF - %s"%(physObj, selLevel),
                               100,-0.5,99.5)

        return
    
    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        directory.cd()

        if self.idLabel is not None:
            self.idLabel.Write()
            self.idLabel_vs_pt.Write()
            self.idLabel_vs_ptRes.Write()
            pass
        self.dxy.Write()
        self.dz.Write()
        self.normChi2.Write()

        return
