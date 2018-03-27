import ROOT as r
from LFVAnalysis.LFVHistograms.PhysObjHistos import PhysObjHistos
from LFVAnalysis.LFVUtilities.utilities import selLevels

class HvyResDaughterHistos:
    def __init__(self, physObj="HvyRes", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        """

        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        self.dR = r.TH1F("%s_%s_dR_%s"%(prefix,physObj,selLevel),
                         "Reco Level %s dR(dau1,dau2) - %s"%(physObj,selLevel),
                         102,-0.05,5.05)

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        directory.cd()
        self.dR.Write()

        return
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

        PhysObjHistos.__init__(self,-1,name,mcType,selLevels[-1])
       
        # Setup Histograms
        self.dict_histosResol = {} #Resolution Histos
        if mcType == "reco":
            self.dict_histosResol[selLevels[-1]] = HvyResMassResolHistos(self.physObjType, selLevels[-1])
        
        self.dict_dauHistos = {} #Daughter Histos
        if mcType == "reco":
            self.dict_dauHistos[selLevels[-1]] = HvyResDaughterHistos(self.physObjType, selLevels[-1], mcType)

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

        outDirPhysObj.mkdir(selLevels[-1])
        dirSelLevel = outDirPhysObj.GetDirectory(selLevels[-1])
        
        if self.mcType == "reco":
            dirSelLevel.mkdir("MassResolution")
            dirMassRes = dirSelLevel.GetDirectory("MassResolution")
            self.dict_histosResol[selLevels[-1]].write(dirMassRes)

        dirSelLevel.mkdir("DaughterHistos")
        dirDauHistos = dirSelLevel.GetDirectory("DaughterHistos")
        if self.mcType == "reco":
            dirDauHistos.mkdir("reco")
            dirReco = dirDauHistos.GetDirectory("reco")
            self.dict_dauHistos[selLevels[-1]].write(dirReco)

        outFile.Close()

        return
