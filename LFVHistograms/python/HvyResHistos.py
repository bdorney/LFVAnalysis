import ROOT as r
from LFVAnalysis.LFVHistograms.PhysObjHistos import PhysObjHistos
from LFVAnalysis.LFVUtilities.utilities import selLevels

class HvyResMassResolHistos:
    def __init__(self, physObj="HvyRes", selLevel="all"):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        """
        
        self.massResol = r.TH1F("h_%s_massResol_%s"%(physObj,selLevel),
                                        "%s mass resolution - %s"%(physObj,selLevel),
                                        100,-2.5,2.5) #(reco - gen) / gen
        
        self.mass_response = r.TH2F("h_%s_massReco_vs_massGen_%s"%(physObj,selLevel),
                                        "%s massReco vs. massGen - %s"%(physObj, selLevel),
                                        3500,-0.5,6999.5,
                                        3500,-0.5,6999.5)

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        directory.cd()
        self.massResol.Write()
        self.mass_response.Write()

        return

class HvyResHistos(PhysObjHistos):
    def __init__(self, name="HvyRes", mcType=None):
        """
        pdgId - particle data group MC id for a particle (e.g. 13 for muon)
        name - Only used for complex objects (e.g. Jets) which don't have a pdgId
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """

        PhysObjHistos.__init__(self,-1,name,mcType)
       
        # Setup Histograms
        self.dict_histosResol= {} #Resolution Histos
        if mcType is "reco":
            for lvl in selLevels:
                self.dict_histosResol[lvl] = HvyResMassResolHistos(self.physObjType, lvl)

        return

    def write(self, filename, option="RECREATE"):
        """
        Creates a TFile using TOption option
        Writes all stored histograms to this TFile
        """

        PhysObjHistos.write(self,filename, option)

        outFile = r.TFile(filename, "UPDATE", "", 1)
        outFile.mkdir(self.physObjType)
        outDirPhysObj = outFile.GetDirectory(self.physObjType)

        for lvl in selLevels:
            outDirPhysObj.mkdir(lvl)
            dirSelLevel = outDirPhysObj.GetDirectory(lvl)
            
            if self.mcType is "reco":
                dirSelLevel.mkdir("MassResolution")
                dirMassRes = dirSelLevel.GetDirectory("MassResolution")
                self.dict_histosResol[lvl].write(dirMassRes)

        outFile.Close()

        return
