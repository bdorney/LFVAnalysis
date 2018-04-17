import ROOT as r
from LFVAnalysis.LFVHistograms.PhysObjHistos import *
from LFVAnalysis.LFVHistograms.identificationHistos import identificationHistos
from LFVAnalysis.LFVUtilities.utilities import selLevels

tauDecayLabels = {
        0:"1 prong + 0 pi0",
        1:"1 prong + 1pi0",
        2:"1 prong + 2pi0s",
        5:"2 prongs + 0pi0",
        6:"2 prongs + 1 pi0s",
        7:"2 prongs + 2 pi0s",
        10:"3 prongs + 0 pi0s",
        11:"3 prongs + 1 pi0"
        }

#tauIdLabels = [
#        "isPF"
#        ]
#tauIdLabels = sorted( tauIdLabels, key=str.lower) #alphabitize this just in case (it might grow)
tauIdLabels = tauDecayLabels.values()

class TauIdHistos(identificationHistos):
    def __init__(self, physObj="mu", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        identificationHistos.__init__(self,tauIdLabels,physObj,selLevel,mcType)
        
        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        # 1D Histograms
        self.decayModeFinding = r.TH1F("%s_%s_decayModeFinding_%s"%(prefix,physObj,selLevel),
                                       "%s decayModeFinding - %s"%(physObj, selLevel),
                                       105,-1.05,1.05)
        self.decayModeFindingNewDMs = r.TH1F("%s_%s_decayModeFindingNewDMs_%s"%(prefix,physObj,selLevel),
                                       "%s decayModeFindingNewDMs - %s"%(physObj, selLevel),
                                       105,-1.05,1.05)
        self.againstMuonTight3 = r.TH1F("%s_%s_againstMuonTight3_%s"%(prefix,physObj,selLevel),
                                       "%s againstMuonTight3 - %s"%(physObj, selLevel),
                                       105,-1.05,1.05)
        self.againstElVLooseMVA6 = r.TH1F("%s_%s_againstElVLooseMVA6_%s"%(prefix,physObj,selLevel),
                                       "%s againstElVLooseMVA6 - %s"%(physObj, selLevel),
                                       105,-1.05,1.05)

        # 2D Histograms
        self.decayModeFinding_NewVsOld = r.TH2F("%s_%s_self.decayModeFinding_NewVsOld_%s"%(prefix,physObj,selLevel),
                                       "%s decayModeFindingNewDMs vs. decayModeFindingOld - %s"%(physObj, selLevel),
                                       105,-1.05,1.05,
                                       105,-1.05,1.05)

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        identificationHistos.write(self,directory)

        directory.cd()
        self.decayModeFinding.Write()
        self.decayModeFindingNewDMs.Write()
        self.againstMuonTight3.Write()
        self.againstElVLooseMVA6.Write()
        self.self.decayModeFinding_NewVsOld.Write()

        return

class TauIsoHistos:
    def __init__(self, physObj="tau", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """

        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        self.tightIsoMVArun2v1DBoldDMwLT = r.TH1F("%s_%s_tightIsoMVArun2v1DBoldDMwLT_%s"%(prefix,physObj,selLevel),
                                                  "%s tightIsoMVArun2v1DBoldDMwLT - %s"%(physObj,selLevel),
                                                  110,-0.05,1.05)

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        directory.cd()
        self.tightIsoMVArun2v1DBoldDMwLT.Write()

        return

class TauHistos(PhysObjHistos):
    def __init__(self, pdgId=15, name=None, mcType=None):
        """
        pdgId - particle data group MC id for a particle (e.g. 13 for muon)
        name - Only used for complex objects (e.g. Jets) which don't have a pdgId
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """

        PhysObjHistos.__init__(self,pdgId,name,mcType)

        # Setup Histograms
        self.dict_histosId = {} # Id Histos
        self.dict_histosIso = {} # Iso Histos
        for lvl in selLevels:
            self.dict_histosId[lvl] = TauIdHistos(self.physObjType, lvl, mcType)
            self.dict_histosIso[lvl] = TauIsoHistos(self.physObjType, lvl, mcType)

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

            dirSelLevel.mkdir("Isolation")
            dirIso = dirSelLevel.GetDirectory("Isolation")
            dirIso.mkdir(self.mcType)
            dirMCLevel_Iso = dirIso.GetDirectory(self.mcType)
            self.dict_histosIso[lvl].write(dirMCLevel_Iso)

        outFile.Close()

        return
