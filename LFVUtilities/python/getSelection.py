from LFVAnalysis.LFVUtilities.utilities import selLevels, supOperators
from LFVAnalysis.LFVUtilities.nesteddict import nesteddict

def getSelection(filename_Sel):
    """
    Returns a nesteddict which contains specifies the selection defined in filename_Sel.
    The structure of the returned nesteddict is:

        selDict[selLvl][branchName]

    Where selLvl is the selection level and branchName is the name of a TBranch of
    the ntuple you are planning on analyzing.

    The inner dictionary stores a tuple for each key of the formw:

        (value, operator)

    The value is the logical comparison defined by operator will make against an
    entry of branchName.  The list of supported operators is given in supOperators.

    The structure of the input file is:

        | selLvl | parentLvl | branchName | Value | Operator |
        | :----: | :-------: | :--------: | :---: | :------: |
        | all | None | mu_ibt_pt | 0 | ge |
        | kin | all | mu_ibt_pt | 53 | ge |
        | kin | all | mu_ibt_eta | 2.4 | fabs-le |

    Each key value for the outer dictionary will inherit from it's parentLvl, e.g.
    For a given key the inner dictionary will be a copy of the parentLvl and then new
    keys will be added to it.

    The text of selLvl and parentLvl is case-insensitive to avoid typos causing an issue.
    """

    ret_sel = nesteddict()

    # Load the selection file
    try:
        file_Sel = open(filename_Sel,'r')
    except IOError as e:
        print "Exception:", e
        print "Failed to open: '%s'"%filename_Sel
    else:
        for idx,line in enumerate(file_Sel):
            # Skip headers"
            if not (idx > 1):
                continue

            # skip commented lines
            if line[0] == "#":
                continue

            # partition the line
            line = line.strip('\n') # remove new lines
            line = line.replace(" ","") # remove spaces
            line = line.replace("\t","") # remove tabs
            selItem = line.split("|")
            selItem.pop() # remove last item (it's '')
            selItem.pop(0) # remove the first item (it's '')

            # Extract the information
            selLvl      = selItem[0].lower()
            parentLvl   = selItem[1].lower()
            branchName  = selItem[2]
            cutVal      = selItem[3]
            operator    = selItem[4]

            # Check to make sure the selLvl is understood
            if selLvl not in selLevels:
                print("selection level '%s' not found in supported selLevels"%selLvl)
                print("please cross-check against supported levels: ", selLevels)
                raise LookupError

            # Check to make sure the parentLvl is understood
            if (parentLvl not in selLevels and parentLvl != "none"):
                print("parent level '%s' not found in supported selLevels"%parentLvl)
                print("please cross-check against supported levels: ", selLevels)
                raise LookupError

            # Check to make sure the operator is understood
            for op in operator.split("-"):
                if op not in supOperators:
                    print("operator '%s' not found in supported operators"%op)
                    print("please cross-check against supported operators: ", supOperators)
                    raise LookupError

            # Store info in the nested dictionary
            if parentLvl == "none": # Case no parent
                ret_sel[selLvl][branchName] = (float(cutVal), operator)
            else: # Case parent exists
                if selLvl in ret_sel.keys(): # Only need to add one entry, key exists already
                    ret_sel[selLvl][branchName] = (float(cutVal), operator)
                else: # key does not exist already, add it and all members of the parent selection level
                    # Check to make sure parentLvl is understood (i.e. maybe user made a typo)
                    if parentLvl not in ret_sel.keys():
                        print("parent level '%s' not found in ret_sel dictionary"%parentLvl)
                        print("please cross-check against known keys: ", ret_sel.keys())
                        raise KeyError
                    
                    # parentLvl is present, add all previous info
                    for bName,cutTuple in ret_sel[parentLvl].iteritems():
                        ret_sel[selLvl][bName] = cutTuple
                        pass

                    # now add the current line
                    ret_sel[selLvl][branchName] = (float(cutVal), operator)
                    pass # end key dos not exist already in dictionary
                pass # end parent exists
            pass # end loop over file
    finally:
        file_Sel.close()
        pass

    # Fill additional sel levels if they are not present using the last filled lvl
    for lvl in selLevels:
        if lvl not in ret_sel.keys():
            lastLvl = (ret_sel.keys())[-1]
            
            for bName,cutTuple in ret_sel[lastLvl].iteritems():
                ret_sel[lvl][bName] = cutTuple

    return ret_sel
