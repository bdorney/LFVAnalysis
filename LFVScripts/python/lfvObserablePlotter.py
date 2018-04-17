#!/bin/env python

if __name__ == '__main__':
    from optparse import OptionGroup, OptionParser
    parser = OptionParser()
    
    # Mandatory Options
    requiredArgsGroup = OptionGroup(
                parser,
                "Required Input Arguments",
                "Mandatory options that specify the inputs"
            )
    requiredArgsGroup.add_option("-i","--infilename", type="string", dest="inFile", default=None,
            help="Comma separated file containing TFiles plots are to be taken from, each line should include one physical filename then a TLegend entry string", metavar="inFile")
    requiredArgsGroup.add_option("--obsverableFile", type="string", dest="obsFile", default=None,
            help="Comma separated file where each line goes as: particle name, observable type, observable name",
            metavar="obsFile")
    requiredArgsGroup.add_option("-o","--outfilename", type="string", dest="outFile", default=None,
            help="output file name containing fit results", metavar="outFile")
    parser.add_option_group(requiredArgsGroup)

    from LFVAnalysis.LFVUtilities.utilities import selLevels
    strSelLvls = "{'%s'"%(selLevels[0])
    for idx,selLvl in enumerate(selLevels):
        if idx==0:
            continue
        strSelLvls += ", '%s'"%selLvl
        pass
    strSelLvls += "}"

    # Optional Control Options
    controlArgsGroup = OptionGroup(
                parser,
                "Optional Control Arguments",
                "Optional arguments that control plotting mode.  Three cases are possible: "
                "1) One line in --infilename and neither --selLvlReco or --selLvlGen supplied, or "
                "2) One line in --infilename and both --selLvlReco and --selLvlGen supplied, or "
                "3) Multiple lines in --infilename and either --selLvlReco or --selLvlGen supplied.",
            )
    controlArgsGroup.add_option("--selLvlGen", type="string", dest="selLvlGen", default=None,
            help="selection level to be used for gen level observables, possible values are from set %s"%(strSelLvls),
            metavar="selLvlGen")
    controlArgsGroup.add_option("--selLvlReco", type="string", dest="selLvlReco", default=None,
            help="selection level to be used for reco level observables, possible values are from set %s"%(strSelLvls),
            metavar="selLvlReco")
    parser.add_option_group(controlArgsGroup)

    # Additional Options
    optionalArgsGroup = OptionGroup(
                parser,
                "Optional Plotting Arguments",
                "Optional arguemnts which control the aesthetic presentation of the output plot"
            )
    optionalArgsGroup.add_option("--drawLeg", action="store_true", dest="drawLeg",
            help="Draw a legend on the created plots", metavar="drawLeg")
    optionalArgsGroup.add_option("--saveImage", action="store_true", dest="saveImage",
            help="For each observable create a *.png and a *.C file", metavar="saveImage")
    optionalArgsGroup.add_option("--setLogY", action="store_true", dest="setLogY",
            help="For each observable use a logarithmic y-axis", metavar="setLogY")
    parser.add_option_group(optionalArgsGroup)
    (options, args) = parser.parse_args()
    
    import os
    if (options.inFile is None or options.obsFile is None):
        print "You must supply an --infilename and an --obsverableFile"
        print "Exiting"
        exit(os.EX_USAGE)

    ##############################################
    # Parse input files
    ##############################################
    # Determine which root files to run over
    try:
        with open(options.inFile, 'r') as runs:
            runList = runs.readlines()
    except Exception as e:
        print "exception occured when trying to open file: '%s'"%(options.inFile)
        print "exception: ", e
        exit(os.EX_DATAERR)
        
    # Strip new line character
    runList = [x.strip('\n') for x in runList]
    
    from LFVAnalysis.LFVUtilities.nesteddict import nesteddict
    dictOfInputFiles = nesteddict()
    for run in runList:
        # Skip commented lines
        if run[0] == "#":
            continue

        lineItems = run.split(",")
        dictOfInputFiles[lineItems[0]]=lineItems[1]
        pass

    # Determine which observables to plot
    try:
        with open(options.obsFile, 'r') as observables:
            obsList = observables.readlines()
    except Exception as e:
        print "exception occured when trying to open file: '%s'"%(options.obsFile)
        print "exception: ", e
        exit(os.EX_DATAERR)
        
    # Strip new line character
    obsList = [x.strip('\n') for x in obsList]

    listOfObsTuples = [] # stores tuples, (particleName, obsType, obsName)
    for obs in obsList:
        # Skip commented lines
        if obs[0] == "#":
            continue

        lineItems = obs.split(",")
        listOfObsTuples.append( (lineItems[0], lineItems[1], lineItems[2]) )
        pass

    ##############################################
    # Make the plots
    ##############################################
    if options.outFile is None:
        options.outFile = options.obsFile.strip('.txt')
        options.outFile += ".root"
    
    from LFVAnalysis.LFVUtilities.plotUtilities import plotObservable
    for idx,obsTuple in enumerate(listOfObsTuples):
        if idx==0:
            rootOpt = "RECREATE"
        else:
            rootOpt = "UPDATE"
            pass
        
        plotObservable(
                dictOfInputFiles = dictOfInputFiles,
                obsName = obsTuple[2],
                obsType = obsTuple[1],
                particleName = obsTuple[0],
                selLvlGen = options.selLvlGen,
                selLvlReco = options.selLvlReco,
                drawLeg = options.drawLeg,
                outFileName = options.outFile,
                outFileOption = rootOpt,
                saveImage = options.saveImage,
                setLogY = options.setLogY
                )
        pass # end loop over observables

    print "All plots made"
