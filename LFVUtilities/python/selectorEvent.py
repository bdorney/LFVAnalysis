from LFVAnalysis.LFVUtilities.utilities import passesCut, supOperators
from LFVAnalysis.LFVUtilities.nesteddict import nesteddict

import os
import ROOT as r

bitRefBranches = [

        ]

eventSelection = nesteddict()

def passesEventFilters(event, selDict, delim="-", listOfBranchNames=None, debug=False):
    """
    Returns true (false) if the event passes (fails) all (any) of the event filters defined in selDict

    event             - entry of a TTree
    selDict           - dictionary where the key value is the name of a TBranch in event
                        and the value is a tuple where the first value is a number and 
                        the second is a string delimited by the 'delim' argument.  This
                        delimited string should be made up entires in the supported 
                        operators list supOperators.  An example dictionary is:
                          
                              ["trig_Flag_HBHENoiseFilter"]  = ( 1, "eq")

    delim             - Character which delimites the string portion of the tuple
                        value stored in selDict
    listOfBranchNames - Optional, List of strings where each element is the name of a
                        Branch in the TTree event comes from
    debug             - If true prints additional debugging information
    """

    # Determine the list of branches
    if listOfBranchNames is None:
        listOfBranchNames = [branch.GetName() for branch in event.GetListOfBranches() ]

    # Loop Over Cuts
    evtPassedAllCuts = 1
    for bName,cutTuple in selDict.iteritems():
        if bName in listOfBranchNames:
            bVal = (getattr( event, bName))[idx]
            if bName in bitRefBranches:
                bVal =  r.getValFromVectorBool( getattr( event, bName), idx)
            evtPassedAllCuts *= passesCut( bVal, cutTuple[0], cutTuple[1].split(delim) )
            if evtPassedAllCuts == 0:
                break #Exit cut loop, one cut failed
        else:
            print "Error branch %s not found in listOfBranchNames"%bName
            print "Please cross-check, the available list of branches:"
            print ""
            print listOfBranchNames
            print ""
            print "exiting"
            exit(os.EX_USAGE)
            pass
        pass

    return evtPassedAllCuts
