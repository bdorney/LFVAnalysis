import ROOT as r
from LFVAnalysis.LFVHistograms.kinematicHistos import *
from LFVAnalysis.LFVHistograms.isolationHistos import *
from LFVAnalysis.LFVUtilities.utilities import selLevels

class PhysObjHistos:
    def __init__(self, pdgId, name=None, mcType=None, specificSelLvl=None):
        """
        pdgId - particle data group MC id for a particle (e.g. 13 for muon)
        name - Only used for complex objects (e.g. Jets) which don't have a pdgId
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        specificSelLvl - Optional, make histograms for only a specific element of
                         selLevels. If not provided all are made
        """

        self.mcType = mcType
        self.selLvl = specificSelLvl

        # Determine particle name
        dict_pdgId = {
            11:"el",
            13:"mu",
            15:"tau",
            32:"Zprime",
            1000016:"rpv"
                }

        self.physObjType = ""
        if name is not None:
            self.physObjType = name
        else:
            self.physObjType = dict_pdgId[pdgId]
        
        # Setup histograms
        self.dict_histosKin = {}
        
        if self.selLvl is None:
            for lvl in selLevels:
                self.dict_histosKin[lvl] = kinematicHistos(self.physObjType, lvl, mcType)
        else:
            self.dict_histosKin[self.selLvl] = kinematicHistos(self.physObjType, self.selLvl, mcType)

        return

    def write(self, filename, option="RECREATE"):
        """
        Creates a TFile using TOption option
        Writes all stored histograms to this TFile
        """
        
        outFile = r.TFile(filename, option, "", 1)
        outFile.mkdir(self.physObjType)
        outDirPhysObj = outFile.GetDirectory(self.physObjType)

        for lvl in selLevels:
            # Should we be doing this for only a specific level?
            if self.selLvl is not None:
                if lvl != self.selLvl: continue 

            outDirPhysObj.mkdir(lvl)
            dirSelLevel = outDirPhysObj.GetDirectory(lvl)
            
            dirSelLevel.mkdir("Kinematics")
            dirKin = dirSelLevel.GetDirectory("Kinematics")

            dirKin.mkdir(self.mcType)
            dirMCLevel = dirKin.GetDirectory(self.mcType)
            self.dict_histosKin[lvl].write(dirMCLevel)

        outFile.Close()

        return
