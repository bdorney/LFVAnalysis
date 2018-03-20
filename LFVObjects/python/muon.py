from LFVAnalysis.LFVObjects.physicsObject import *

import ROOT as r

class Muon(PhysObj):
    def __init__(self, px, py, pz, E):
        PhysObj.__init__(self, px, py, pz, E, 13)

        # Id Variables
        self.isGlobal     = -1
        self.isHighPt     = -1
        self.isLoose      = -1
        self.isMedium     = -1
        self.isPF         = -1
        self.isSoft       = -1
        self.isStandAlone = -1
        self.isTight      = -1
        self.isTracker    = -1

        # Iso Variables
        self.isoTrackerBased03 = -1e10

        # Track quality
        self.normChi2 = -1e10
        self.numHitsPix = -1e10
        self.numHitsTrk = -1e10
        self.numMatchedMuStations = -1e10

        return

