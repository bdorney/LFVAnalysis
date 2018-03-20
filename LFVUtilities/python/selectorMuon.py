from LFVAnalysis.LFVObjects.muon import Muon 
from LFVAnalysis.LFVUtilities.utilities import passesCut, selLevels, supOperators
from LFVAnalysis.LFVUtilities.nesteddict import nesteddict

import math as m
import os
import ROOT as r

bitRefBranches = [
        "mu_isGlobalMuon",
        "mu_isHighPtMuon",
        "mu_isLooseMuon",
        "mu_isMediumMuon",
        "mu_isPFMuon",
        "mu_isSoftMuon",
        "mu_isStandAloneMuon"
        "mu_isTightMuon",
        "mu_isTrackerMuon"
        ]

muonSelection = nesteddict()

for lvl in selLevels:
    muonSelection[lvl] = {}

# All Selection - Note there's a "bug" in the NTuples where initial values are -1000 
muonSelection["all"]["mu_ibt_pt"] = (0, "ge")

# Kinematic Selection
for bName,cutTuple in muonSelection["all"].iteritems():
    muonSelection["kin"][bName] = cutTuple
muonSelection["kin"]["mu_ibt_pt"] = (53, "ge")
muonSelection["kin"]["mu_ibt_eta"] = (2.4, "fabs-le")

# Kinematic & Id Selection
muonSelection["kinId"]["mu_isHighPtMuon"] = (1,"eq")
for bName,cutTuple in muonSelection["kin"].iteritems():
    muonSelection["kinId"][bName] = cutTuple

# Kinematic, Id & Isolation Selection
muonSelection["kinIdIso"]["mu_isoTrackerBased03"] = (0.1, "l" )
for bName,cutTuple in muonSelection["kinId"].iteritems():
    muonSelection["kinIdIso"][bName] = cutTuple

def getSelectedMuons(event, selDict, numMuons, delim="-", listOfBranchNames=None, useGlobalTrack=False, debug=False):
    """
    Returns a list of Muons passing selection defined in selDict 

    event             - entry of a TTree
    selDict           - dictionary where the key value is the name of a TBranch in event
                        and the value is a tuple where the first value is a number and 
                        the second is a string delimited by the 'delim' argument.  This
                        delimited string should be made up entires in the supported 
                        operators list supOperators.  An example dictionary is:
                          
                              ["pt"]  = ( 10, "g")
                              ["eta"] = ( 2.4, "fabs-le")

    numMouns          - Number of Muons in event
    delim             - Character which delimites the string portion of the tuple
                        value stored in selDict
    listOfBranchNames - Optional, List of strings where each element is the name of a
                        Branch in the TTree event comes from
    useGlobalTrack    - If true (false) stores the global (ibt) track info
    debug             - If true prints additional debugging information
    """

    # Determine the list of branches
    if listOfBranchNames is None:
        listOfBranchNames = [branch.GetName() for branch in event.GetListOfBranches() ]

    # Consistency Check on length
    if numMuons != len( getattr(event, selDict.keys()[0])):
        if debug:
            print "numMuons = %i"%(numMuons)
            print "Error numMuons != length of branch %s"%(selDict.keys()[0])
            print "Resetting numMuons to %i, undefined behavior may occur!!!"%(len( getattr(event, selDict.keys()[0])))
        numMuons = len( getattr(event, selDict.keys()[0]))

    # Loop Over physics objects in the event
    if debug:
        print "Muons"
        print "| idx | px | py | pz | E |"
        print "| --- | -- | -- | -- | - |"
    
    ret_muons = []
    for idx in range(0,numMuons):
        muonPassedAllCuts = 1

        # Loop Over Cuts
        for bName,cutTuple in selDict.iteritems():
            if bName in listOfBranchNames:
                bVal = (getattr( event, bName))[idx]
                if bName in bitRefBranches:
                    bVal =  r.getValFromVectorBool( getattr( event, bName), idx)
                muonPassedAllCuts *= passesCut( bVal, cutTuple[0], cutTuple[1].split(delim) )
                if muonPassedAllCuts == 0:
                    break #Exit cut loop, one cut failed
            else:
                print "Error branch %s not found in listOfBranchNames"%bName
                print "Please cross-check, the available list of branches:"
                print ""
                print listOfBranchNames
                print ""
                print "exiting"
                exit(os.EX_USAGE)

        # Check if selection passed, if so append a muon to the list
        if muonPassedAllCuts == True:
            # Determine Energy for 4-vector
            energy = m.sqrt( event.mu_ibt_px[idx]**2 + 
                             event.mu_ibt_py[idx]**2 +
                             event.mu_ibt_pz[idx]**2 +
                             0.1056583745**2)

            # Make the Muon
            thisMuon = Muon(event.mu_ibt_px[idx],
                            event.mu_ibt_py[idx],
                            event.mu_ibt_pz[idx],
                            energy)
    
            thisMuon.charge = event.mu_ibt_charge[idx]

            # Store impact parameters
            thisMuon.dxy = event.mu_ibt_dxy[idx]
            thisMuon.dz = event.mu_ibt_dz[idx]
                
            # track fit info
            thisMuon.normChi2 = event.mu_ibt_normalizedChi2[idx]
            
            if useGlobalTrack:
                # Determine Energy for 4-vector using the global track instead
                energy = m.sqrt( event.mu_gt_px[idx]**2 + 
                                 event.mu_gt_py[idx]**2 +
                                 event.mu_gt_pz[idx]**2 +
                                 0.1056583745**2)

                # Update the four-vector
                thisMuon.setPxPyPzE(event.mu_gt_px[idx],
                                event.mu_gt_py[idx],
                                event.mu_gt_pz[idx],
                                energy)

                # Store charge from global track instead
                thisMuon.charge = event.mu_gt_charge[idx]
                
                # Store impact parameters from global track instead
                thisMuon.dxy = event.mu_gt_dxy[idx]
                thisMuon.dz = event.mu_gt_dz[idx]
                
                # track fit info
                thisMuon.normChi2 = event.mu_gt_normalizedChi2[idx]

            
            # Store Other Properties

            # Try getting muon type using boost python (doesn't work...), curse you std::vector<bool>
            #import pluginvectorBoolParser # From LFVUtilities/plugins
            #boolParser = pluginvectorBoolParser.parseVectorBool()
            #thisMuon.isGlobal     = boolParser.parse(event.mu_isGlobalMuon, idx)
            #thisMuon.isHighPt     = boolParser.parse(event.mu_isHighPtMuon, idx)
            #thisMuon.isLoose      = boolParser.parse(event.mu_isLooseMuon, idx)
            #thisMuon.isMedium     = boolParser.parse(event.mu_isMediumMuon, idx)
            #thisMuon.isPF         = boolParser.parse(event.mu_isPFMuon, idx)
            #thisMuon.isSoft       = boolParser.parse(event.mu_isSoftMuon, idx)
            #thisMuon.isStandAlone = boolParser.parse(event.mu_isStandAloneMuon, idx)
            #thisMuon.isTight      = boolParser.parse(event.mu_isTightMuon, idx)
            #thisMuon.isTracker    = boolParser.parse(event.mu_isTrackerMuon, idx)

            # Try getting muon type using ROOT macro, curse you std::vector<bool>
            #cmssw_base = os.getenv("CMSSW_BASE")
            #r.gROOT.LoadMacro('%s/src/LFVAnalysis/LFVUtilities/include/getValFromVectorBool.h+'%cmssw_base)
            thisMuon.isGlobal     = r.getValFromVectorBool(event.mu_isGlobalMuon, idx)
            thisMuon.isHighPt     = r.getValFromVectorBool(event.mu_isHighPtMuon, idx)
            thisMuon.isLoose      = r.getValFromVectorBool(event.mu_isLooseMuon, idx)
            thisMuon.isMedium     = r.getValFromVectorBool(event.mu_isMediumMuon, idx)
            thisMuon.isPF         = r.getValFromVectorBool(event.mu_isPFMuon, idx)
            thisMuon.isSoft       = r.getValFromVectorBool(event.mu_isSoftMuon, idx)
            thisMuon.isStandAlone = r.getValFromVectorBool(event.mu_isStandAloneMuon, idx)
            thisMuon.isTight      = r.getValFromVectorBool(event.mu_isTightMuon, idx)
            thisMuon.isTracker    = r.getValFromVectorBool(event.mu_isTrackerMuon, idx)
            
            thisMuon.isoTrackerBased03 = event.mu_isoTrackerBased03[idx]
            
            thisMuon.numHitsPix = event.mu_numberOfValidPixelHits[idx]
            thisMuon.numHitsTrk = event.mu_trackerLayersWithMeasurement[idx]
            thisMuon.numMatchedMuStations = event.mu_numberOfMatchedStations[idx]

            if debug:
                print "| %i | %f | %f | %f | %f |"%(idx, thisMuon.px(), thisMuon.py(), thisMuon.pz(), thisMuon.E())

            # Append thisMuon to the list of returned muons
            ret_muons.append(thisMuon)

    return ret_muons
