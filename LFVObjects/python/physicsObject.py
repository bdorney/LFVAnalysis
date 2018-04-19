from LFVAnalysis.LFVUtilities.utilities import dR

import ROOT as r

class PhysObj:
    def __init__(self, px, py, pz, E, pdgId=-1, status=-1):
        # Electric Charge
        self.charge = -1e10 #electric charge of candidate

        # Impact Parameters
        self.dxy = -1e10    #transverse impact parameter
        self.dz = -1e10     #longitudinal impact parameter

        # Four Vector
        self.fourVector = r.TLorentzVector(px, py, pz, E)

        # Particle Id
        self.pdgId = pdgId

        # MC Status Code
        self.status = status
        
        # Generator level match
        self.isMatched = False
        self.dR = -1

        return

    def setMatchedGenObj(self, PhysObjGen):
        """
        PhysObjGen - a generator level object to be matched to this object
        """

        self.matchedGenObj = PhysObjGen
        self.isMatched = True
        PhysObjGen.isMatched = True
        self.dR = dR(self, PhysObjGen)

        return

    def setPxPyPzE(self, px, py, pz, E):
        self.fourVector.SetPxPyPzE(px,py,pz,E)
        return

    def setPtEtaPhiM(self, pt, eta, phi, M):
        self.fourVector.SetPtEtaPhiM(pt, eta, phi, M)
        return

    def setPtEtaPhiE(self, pt, eta, phi, E):
        self.fourVector.SetPtEtaPhiE(pt, eta, phi, E)
        return

    def E(self):
        return self.fourVector.E()
  
    def eta(self):
        cosTheta = self.fourVector.CosTheta()
        if ( (cosTheta*cosTheta) < 1): # otherwise spits out warnings
            return self.fourVector.Eta()
        else:
            if self.pz() > 0:
                return 10e10
            else: 
                return -10e10

    def phi(self):
        return self.fourVector.Phi()

    def px(self):
        return self.fourVector.Px()
    
    def py(self):
        return self.fourVector.Py()

    def pz(self):
        return self.fourVector.Pz()

    def pt(self):
        return self.fourVector.Pt()

    def M(self):
        return self.fourVector.M()
