from LFVAnalysis.LFVObjects.physicsObject import *

import ROOT as r

class Tau(PhysObj):
    def __init__(self, px, py, pz, E):
        PhysObj.__init__(self, px, py, pz, E, 15)

        # Id Variables
        self.againstElectronVLooseMVA6 = -1e10
        self.againstMuonTight3 = -1e10
        self.decayModeFinding = -1e10

        # Isolation
        self.byTightIsolationMVArun2v1DBoldDMwLT = -1e10

        return

