import os

# Selection Levels
selLevels = (
        "all",
        "kin",
        "kinId",
        "kinIdIso"
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

def fillKinematicHistos(candidate, kinHistos):
    """
    Fills kinematic histos for an particle candidate.
    Note multiplicity histo is not filled

    candidate - an object inheriting from PhysObj
    kinHistos - an instance of kinematicHistos
    """

    kinHistos.charge.Fill(candidate.charge)
    kinHistos.energy.Fill(candidate.E())
    kinHistos.eta.Fill(candidate.eta())
    kinHistos.mass.Fill(candidate.M())
    kinHistos.pt.Fill(candidate.pt())
    kinHistos.pz.Fill(candidate.pz())

    return
    
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
