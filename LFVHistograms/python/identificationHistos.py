import ROOT as r

class identificationHistos:
    def __init__(self, listIdLabels, physObj="mu", selLevel="all", mcType=None):
        """
        listIdLabels - list of strings specifying ID labels
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        # Make the label histogram and set the labels
        self.idLabel = r.TH1F("%s_%s_idLabel_%s"%(prefix,physObj,selLevel),
                              "%s Id Label - %s"%(physObj, selLevel), 
                              len(listIdLabels),0.5,len(listIdLabels)+0.5
                              )
        for binX,label in enumerate(listIdLabels):
            self.idLabel.GetXaxis().SetBinLabel(binX+1,label)

        # Make impact parameter histograms
        self.dxy = r.TH1F("%s_%s_dxy_%s"%(prefix,physObj,selLevel),
                          "%s d_{xy} - %s"%(physObj, selLevel),
                          100,-0.5,9.5)
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

        self.idLabel.Write()
        self.dxy.Write()
        self.dz.Write()
        self.normChi2.Write()

        return
