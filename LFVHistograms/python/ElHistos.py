import ROOT as r
from LFVAnalysis.LFVHistograms.PhysObjHistos import PhysObjHistos
from LFVAnalysis.LFVHistograms.identificationHistos import identificationHistos
from LFVAnalysis.LFVUtilities.utilities import selLevels

# This follows the class method names for access with getattr(...) in code
elIdLabels = [
        "isHEEP"
        ]
elIdLabels = sorted( elIdLabels, key=str.lower) #alphabitize this just in case

class ElIdHistos(identificationHistos):
    def __init__(self, physObj="el", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        identificationHistos.__init__(self,elIdLabels,physObj,selLevel,mcType)
        
        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        identificationHistos.write(self,directory)

        return

class ElHistos(PhysObjHistos):
    def __init__(self, pdgId=11, name=None, mcType=None):
        """
        pdgId - particle data group MC id for a particle (e.g. 13 for muon)
        name - Only used for complex objects (e.g. Jets) which don't have a pdgId
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        PhysObjHistos.__init__(self,pdgId,name,mcType)

        # Setup Histograms
        self.dict_histosId = {} #Id Histos
        for lvl in selLevels:
            self.dict_histosId[lvl] = ElIdHistos(self.physObjType, lvl, mcType)

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
            
            dirSelLevel.mkdir("Identification")
            dirId = dirSelLevel.GetDirectory("Identification")
            dirId.mkdir(self.mcType)
            dirMCLevel_Id = dirId.GetDirectory(self.mcType)
            self.dict_histosId[lvl].write(dirMCLevel_Id)

        outFile.Close()

        return
