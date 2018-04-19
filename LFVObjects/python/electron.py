from LFVAnalysis.LFVObjects.physicsObject import *

import ROOT as r

class Electron(PhysObj):
    def __init__(self, px, py, pz, E):
        PhysObj.__init__(self, px, py, pz, E, 11)

        # Id Variables
        self.isHEEP = -1

        # Track quality
        #self.normChi2 = -1e10
        
        return

