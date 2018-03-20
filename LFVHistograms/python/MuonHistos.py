import ROOT as r
from LFVAnalysis.LFVHistograms.PhysObjHistos import PhysObjHistos
from LFVAnalysis.LFVHistograms.identificationHistos import identificationHistos
from LFVAnalysis.LFVUtilities.utilities import selLevels

# This follows the class method names for access with getattr(...) in code
muonIdLabels = [
        "isGlobal",
        "isHighPt",
        "isLoose",
        "isMedium",
        "isPF",
        "isSoft",
        "isStandAlone",
        "isTight",
        "isTracker"
        ]
muonIdLabels = sorted( muonIdLabels, key=str.lower) #alphabitize this just in case

muonhitLabels = [
        "numHitsPix",
        "numHitsTrk",
        "numMatchedMuStations"
        ]
muonhitLabels = sorted( muonhitLabels, key=str.lower) #alphabitize

class MuonIdHistos(identificationHistos):
    def __init__(self, physObj="mu", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        identificationHistos.__init__(self,muonIdLabels,physObj,selLevel,mcType)
        
        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        self.dict_hitHistos = {}
        for idLabel in muonIdLabels:
            self.dict_hitHistos[idLabel] = r.TH2F("%s_%s_hitInfo_%s_%s"%(prefix,physObj,idLabel,selLevel),
                                                  "%s Hit Info for %s - %s"%(physObj, idLabel, selLevel),
                                                   50,-0.5,49.5,
                                                   len(muonhitLabels),0.5,len(muonhitLabels)+0.5)
            for binY,hitLabel in enumerate(muonhitLabels):
                self.dict_hitHistos[idLabel].GetYaxis().SetBinLabel(binY+1,hitLabel)

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        identificationHistos.write(self,directory)

        directory.cd()
        for idLabel in muonIdLabels:
            self.dict_hitHistos[idLabel].Write()

        return

class MuonIsoHistos:
    def __init__(self, physObj="mu", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """
        
        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        self.isoTrackerBased03 = r.TH1F("%s_%s_isoTrkBased03_%s"%(prefix,physObj,selLevel),
                                        "%s isoTrkBased03 - %s"%(physObj,selLevel),
                                        400,-0.5,99.5)

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """

        directory.cd()
        self.isoTrackerBased03.Write()

        return

class MuonHistos(PhysObjHistos):
    def __init__(self, pdgId=13, name=None, mcType=None):
        """
        pdgId - particle data group MC id for a particle (e.g. 13 for muon)
        name - Only used for complex objects (e.g. Jets) which don't have a pdgId
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """

        PhysObjHistos.__init__(self,pdgId,name,mcType)
        
        # Setup Histograms
        self.dict_histosId = {} #Id Histos
        self.dict_histosIso= {} #Iso Histos
        for lvl in selLevels:
            self.dict_histosId[lvl] = MuonIdHistos(self.physObjType, lvl, mcType)
            self.dict_histosIso[lvl]= MuonIsoHistos(self.physObjType, lvl, mcType)

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
            self.dict_histosId[lvl].write(dirId)

            dirSelLevel.mkdir("Isolation")
            dirIso = dirSelLevel.GetDirectory("Isolation")
            self.dict_histosIso[lvl].write(dirIso)

        outFile.Close()

        return
