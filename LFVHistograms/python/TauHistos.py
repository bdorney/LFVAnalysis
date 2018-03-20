import ROOT as r
from LFVAnalysis.LFVHistograms.PhysObjHistos import *
from LFVAnalysis.LFVUtilities.utilities import selLevels

class TauHistos(PhysObjHistos):
    def __init__(self, pdgId=15, name=None, mcType=None):
        """
        pdgId - particle data group MC id for a particle (e.g. 13 for muon)
        name - Only used for complex objects (e.g. Jets) which don't have a pdgId
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """

        PhysObjHistos.__init__(self,pdgId,name,mcType)

        return
