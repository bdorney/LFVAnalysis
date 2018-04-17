from LFVAnalysis.LFVObjects.physicsObject import *

import ROOT as r

class Tau(PhysObj):
    def __init__(self, px, py, pz, E):
        PhysObj.__init__(self, px, py, pz, E, 15)

        # Id Variables
        self.againstElectronVLooseMVA6 = -1e10
        self.againstMuonTight3 = -1e10
        
        self.decayMode = -1
        self.decayModeFinding = -1e10
        self.decayModeFindingNewDMs = -1e10

        self.isPF = -1e10

        # Isolation
        self.byTightIsolationMVArun2v1DBoldDMwLT = -1e10
        self.byTightIsolationMVArun2v1DBnewDMwLT = -1e10    # New decay mode 

        return
