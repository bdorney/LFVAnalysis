from LFVAnalysis.LFVObjects.electron import Electron
from LFVAnalysis.LFVUtilities.utilities import passesCut, selLevels, supOperators
from LFVAnalysis.LFVUtilities.nesteddict import nesteddict

import math as m
import os
import ROOT as r

bitRefBranches = [
        "gsf_isHeepV7"
        ]

elSelection = nesteddict()

for lvl in selLevels:
    elSelection[lvl] = {}

# No Selection (need to fill this to have the dict not empty)
elSelection["all"]["gsf_energy"] = (0, "ge")

# Kinematic Selection
elSelection["kin"]["gsf_energy"] = (50, "g")
#elSelection["kin"]["gsf_eta"] = (2.4, "fabs-le")

# Kinematic & Id Selection
#elSelection["kinId"]["mu_isGlobalMuon"] = (1,"eq")
for bName,cutTuple in elSelection["kin"].iteritems():
    elSelection["kin-id"][bName] = cutTuple

# Kinematic, Id & Isolation Selection
#elSelection["kinIdIso"]["mu_isoTrackerBased03"] = (0.1, "l" )
for bName,cutTuple in elSelection["kin-id"].iteritems():
    elSelection["kin-id-iso"][bName] = cutTuple

def getSelectedElectrons(event, selDict, numElectrons, delim="-", listOfBranchNames=None, debug=False):
    """
    Returns a list of Electrons passing selection defined in selDict 

    event             - entry of a TTree
    selDict           - dictionary where the key value is the name of a TBranch in event
                        and the value is a tuple where the first value is a number and 
                        the second is a string delimited by the 'delim' argument.  This
                        delimited string should be made up entires in the supported 
                        operators list supOperators.  An example dictionary is:
                          
                              ["pt"]  = ( 10, "g")
                              ["eta"] = ( 2.4, "fabs-le")

    numElectrons      - Number of Electrons in event
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
    if numElectrons != len( getattr(event, selDict.keys()[0])):
        if debug:
            print "numElectrons = %i"%(numElectrons)
            print "Error numElectrons != length of branch %s"%(selDict.keys()[0])
            print "Resetting numElectrons to %i, undefined behavior may occur!!!"%(len( getattr(event, selDict.keys()[0])))
        numElectrons = len( getattr(event, selDict.keys()[0]))
    
    # Loop Over physics objects in the event
    if debug:
        print "Electrons"
        print "| idx | px | py | pz | E |"
        print "| --- | -- | -- | -- | - |"
    
    ret_electrons = []
    for idx in range(0,numElectrons):
        electronPassedAllCuts = 1

        # Loop Over Cuts
        for bName,cutTuple in selDict.iteritems():
            if bName in listOfBranchNames:
                bVal = (getattr( event, bName))[idx]
                if bName in bitRefBranches:
                    bVal =  r.getValFromVectorBool( getattr( event, bName), idx)
                electronPassedAllCuts *= passesCut( bVal, cutTuple[0], cutTuple[1].split(delim) )
                if electronPassedAllCuts == 0:
                    break #Exit cut loop, one cut failed
            else:
                print "Error branch %s not found in listOfBranchNames"%bName
                print "Please cross-check, the available list of branches:"
                print ""
                print listOfBranchNames
                print ""
                print "exiting"
                exit(os.EX_USAGE)

        # Check if selection passed, if so append an electron to the list
        if electronPassedAllCuts == True:
            # Make the Electron
            thisElectron = Electron(
                        event.gsf_px[idx],
                        event.gsf_py[idx],
                        event.gsf_pz[idx],
                        event.gsf_energy[idx]
                    )

            # Store Other Properties
            thisElectron.charge = event.gsf_charge[idx]
            thisElectron.dxy = event.gsf_dxy[idx]
            thisElectron.dz = event.gsf_dz[idx]

            thisElectron.isHEEP = r.getValFromVectorBool(event.gsf_isHeepV7, idx)
            
            if debug:
                print "| %i | %f | %f | %f | %f |"%(idx, thisElectron.px(), thisElectron.py(), thisElectron.pz(), thisElectron.E())
            
            # Append thisElectron to the list of returned electrons
            ret_electrons.append(thisElectron)

    return ret_electrons
