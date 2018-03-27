from LFVAnalysis.LFVObjects.tau import Tau
from LFVAnalysis.LFVUtilities.utilities import passesCut, selLevels, supOperators
from LFVAnalysis.LFVUtilities.nesteddict import nesteddict

import math as m
import os
import ROOT as r

bitRefBranches = [
        "tau_isPFTau",
        "tau_hasSecondaryVertex"
        ]

tauSelection = nesteddict()

for lvl in selLevels:
    tauSelection[lvl] = {}

# No Selection (need to fill this to have the dict not empty)
tauSelection["all"]["tau_pt"] = (0, "ge")

# Kinematic Selection
tauSelection["kin"]["tau_pt"] = (30, "ge")
tauSelection["kin"]["tau_eta"] = (2.3, "fabs-le")

# Kinematic & Id Selection
tauSelection["kinId"]["tau_decayModeFinding"] = (0.5, "ge")
tauSelection["kinId"]["tau_againstMuonTight3"] = (0.5, "ge")
tauSelection["kinId"]["tau_againstElectronVLooseMVA6"] = (0.5, "ge")
tauSelection["kinId"]["tau_charge"] = (1, "fabs-eq")
for bName,cutTuple in tauSelection["kin"].iteritems():
    tauSelection["kinId"][bName] = cutTuple

# Kinematic, Id & Isolation Selection
tauSelection["kinIdIso"]["tau_byTightIsolationMVArun2v1DBoldDMwLT"] = (0.5, "g" )
for bName,cutTuple in tauSelection["kinId"].iteritems():
    tauSelection["kinIdIso"][bName] = cutTuple

def getSelectedTaus(event, selDict, numTaus, delim="-", listOfBranchNames=None, debug=False):
    """
    Returns a list of Taus passing selection defined in selDict 

    event             - entry of a TTree
    selDict           - dictionary where the key value is the name of a TBranch in event
                        and the value is a tuple where the first value is a number and 
                        the second is a string delimited by the 'delim' argument.  This
                        delimited string should be made up entires in the supported 
                        operators list supOperators.  An example dictionary is:
                          
                              ["pt"]  = ( 10, "g")
                              ["eta"] = ( 2.4, "fabs-le")

    numTaus           - Number of Taus in event
    delim             - Character which delimites the string portion of the tuple
                        value stored in selDict
    listOfBranchNames - Optional, List of strings where each element is the name of a
                        Branch in the TTree event comes from
    debug             - If true prints additional debugging information
    """

    # Determine the list of branches
    if listOfBranchNames is None:
        listOfBranchNames = [branch.GetName() for branch in event.GetListOfBranches() ]

    # Consistency Check on length
    if numTaus != len( getattr(event, selDict.keys()[0])):
        print "Error numTaus != length of branch %s"%(selDict.keys()[0])
        print "Resetting numTaus, undefined behavior may occur!!!"
        numTaus = len( getattr(event, selDict.keys()[0]))
    
    # Loop Over physics objects in the event
    if debug:
        print "Taus"
        print "| idx | px | py | pz | E |"
        print "| --- | -- | -- | -- | - |"
    
    ret_taus = []
    for idx in range(0,numTaus):
        tauPassedAllCuts = 1

        # Loop Over Cuts
        for bName,cutTuple in selDict.iteritems():
            if bName in listOfBranchNames:
                bVal = (getattr( event, bName))[idx]
                if bName in bitRefBranches:
                    bVal =  r.getValFromVectorBool( getattr( event, bName), idx)
                tauPassedAllCuts *= passesCut( bVal, cutTuple[0], cutTuple[1].split(delim) )
                if tauPassedAllCuts == 0:
                    break #Exit cut loop, one cut failed
            else:
                print "Error branch %s not found in listOfBranchNames"%bName
                print "Please cross-check, the available list of branches:"
                print ""
                print listOfBranchNames
                print ""
                print "exiting"
                exit(os.EX_USAGE)

        # Check if selection passed, if so append a tau to the list
        if tauPassedAllCuts == True:
            # Make the Tau
            thisTau = Tau(  event.tau_px[idx],
                            event.tau_py[idx],
                            event.tau_pz[idx],
                            event.tau_energy[idx])

            # Store Other Properties
            thisTau.charge = event.tau_charge[idx]

            thisTau.isPF = r.getValFromVectorBool(event.tau_isPFTau, idx)

            thisTau.againstElectronVLooseMVA6 = event.tau_againstElectronVLooseMVA6[idx]
            thisTau.againstMuonTight3 = event.tau_againstMuonTight3[idx]
            thisTau.decayModeFinding = event.tau_decayModeFinding[idx]
            
            thisTau.dxy = event.tau_dxy[idx]
            
            thisTau.byTightIsolationMVArun2v1DBoldDMwLT = event.tau_byTightIsolationMVArun2v1DBoldDMwLT[idx]

            if debug:
                print "| %i | %f | %f | %f | %f |"%(idx, thisTau.px(), thisTau.py(), thisTau.pz(), thisTau.E())
            
            # Append thisTau to the list of returned taus
            ret_taus.append(thisTau)

    return ret_taus
