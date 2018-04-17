import os

# Selection Levels
selLevels = (
        "all",
        "kin",
        "kin-id",
        "kin-id-iso"
        )

# Monte Carlo Levels
mcLevels = (
        "gen",
        "reco"
        )

# Supported Operators
supOperators = (
        "eq",   #equals
        "fabs", #absolute value
        "g",    #greater than
        "ge",   #greater or equal too
        "l",    #less than
        "le"    #less than or equal too
        )

# Supported Observable Types
supObservables = {
        "DaughterHistos":[
            "dR"
            ],
        "Kinematics":[
            "charge",
            "energy",
            "eta",
            "mass",
            "multi",
            "pt",
            "pz"
            ],
        "Identification":[
            "againstElVLooseMVA6",
            "againstMuonTight3",
            "decayModeFinding",
            "dxy",
            "dz",
            "idLabel",
            "normChi2",
            ],
        "Isolation":[
            "isoTrkBased03",
            "tightIsoMVArun2v1DBoldDMwLT"
            ],
        "MassResolution":[
            "massResol"
            ]
        }

# Supported Particle Names
supParticleNames = (
        "el",       # electron
        "HvyRes",   # heavy resonance candidate (e.g. RPV, QBH, Zprime, etc...)
        "mu",       # muon
        "tau"       # tau
        )

def calcObsResolution(obsReco, obsGen):
    """
    Calculates the resolution for some observable
    """

    return (obsReco - obsGen) / obsGen

def dR(cand1, cand2):
    """
    Calculates the dR between cand1 and cand2

    cand1 - an object inheriting from PhysObj
    cand2 - an object inheriting from PhysObj
    """

    from math import sqrt

    return sqrt( (cand1.eta() - cand2.eta())**2 + (cand1.phi() - cand2.phi())**2 )

def fillKinematicHistos(candidate, kinHistos, fillGen=True):
    """
    Fills kinematic histos for an particle candidate.
    Note multiplicity histo is not filled

    candidate - an object inheriting from PhysObj
    kinHistos - an instance of kinematicHistos
    fillGen   - True (False) will (not) fill histograms requiring GEN lvl info
    """

    kinHistos.charge.Fill(candidate.charge)
    kinHistos.energy.Fill(candidate.E())
    kinHistos.eta.Fill(candidate.eta())
    kinHistos.mass.Fill(candidate.M())
    kinHistos.pt.Fill(candidate.pt())
    kinHistos.pz.Fill(candidate.pz())
    if fillGen:
        kinHistos.dRMatched.Fill(dR(candidate, candidate.matchedGenObj))
        kinHistos.ptRes.Fill(calcObsResolution(candidate.pt(), candidate.matchedGenObj.pt() ) )
        pass

    return

def matchObjsBydR(listReco,listGen,maxdR=0.5,debug=False):    
    """
    Matches objects in listGen to objects in listReco by dR matching.
    The best match will be used. A match is found if:

        dR(listReco[i],listGen[j]) < maxdR

    And
        
        dR(listReco[i],listGen[j]) is the minimum dR

    Note elements of listReco and listGen are expected to inherit from
    PhysObj of LFVObjects/python/physicsObject.py
    """

    import numpy as np

    # Determine all possible dR pairings
    listPossibleMatches = [ ] # list of tuples: (dR, idxReco, idxGen)
    for idxReco, candReco in enumerate(listReco):
        for idxGen, candGen in enumerate(listGen):
            listPossibleMatches.append( (dR(candReco, candGen), idxReco, idxGen) )
            pass
        pass

    # store the pairings in a structured numpy array
    dataType = np.dtype('float,int,int')
    dataType.names = ["dR","idxReco","idxGen"]
    arrayPossibleMatches = np.array(listPossibleMatches, dataType) 
    
    # remove entries failing the cut
    arrayPossibleMatches = arrayPossibleMatches[ arrayPossibleMatches['dR'] < maxdR]

    # sort possible matches by ascending dR
    arrayPossibleMatches = np.sort(arrayPossibleMatches)

    for matchCand in arrayPossibleMatches:
        #print matchCand
        if listReco[matchCand['idxReco']].isMatched: # Set when matched below
            continue
        elif listGen[matchCand['idxGen']].isMatched: # Set when matched below
            continue
        else:
            listReco[matchCand['idxReco']].setMatchedGenObj(listGen[matchCand['idxGen']])
            if debug:
                print "matchObjsBydR() - match found (%f, %i, %i)"%(matchCand['dR'], matchCand['idxReco'], matchCand['idxGen'])
                pass # end debug
            pass # end matching
        pass # end loop over arrayPossibleMatches

    return arrayPossibleMatches

def passesCut(valOfInterest, cutVal, listOfCutStrings):
    """
    Checks if valOfInterest passes cutVal uses logical operations
    defined in listOfCutStrings

    valOfInterest   - numeric value to be checked if passes cut
    cutVal          - value to compare valOfInterest against
    listOfCutStrings- list of strings to form a logical comparison with.
                      Note that elements must be in supOperators and 
                      length must be <= 2.
    
    Returns True (False) if valOfInterest passes (fails) listOfCutStrings
    """

    if len(listOfCutStrings) > 2:
        print "list of cut strings longer than expected, given:"
        print ""
        print listOfCutStrings
        print ""
        print "exiting"
        exit(os.EX_USAGE)

    for operator in listOfCutStrings:
        if operator not in supOperators:
            print "Operator %s not understood"
            print "The list of supported operators is:"
            print ""
            print supOperators
            print ""
            print "exiting"
            exit(os.EX_USAGE)

    if 'fabs' in listOfCutStrings:
        valOfInterest = abs(valOfInterest)
        listOfCutStrings.remove('fabs')

    if "eq" in listOfCutStrings:
        return (valOfInterest == cutVal)
    elif "g" in listOfCutStrings:
        return (valOfInterest > cutVal)
    elif "ge" in listOfCutStrings:
        return (valOfInterest >= cutVal)
    elif "l" in listOfCutStrings:
        return (valOfInterest < cutVal)
    elif "le" in listOfCutStrings:
        return (valOfInterest <= cutVal)
