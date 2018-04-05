def getCyclicColor(idx, modulo=10, colors=None):
    """
    Returns a color based on modular division of an index

    idx     - current index

    modulo - base for modular division, e.g. idx % modulo

    colors - dictionary where key value is an integer and 
             value is a ROOT color (e.g. kBlack)
    """
    import ROOT as r

    if colors is None:
        colors = {
                0:r.kBlack,
                1:r.kGreen-1,
                2:r.kRed-1,
                3:r.kBlue-1,
                4:r.kGreen-2,
                5:r.kRed-2,
                6:r.kBlue-2,
                7:r.kGreen-3,
                8:r.kRed-3,
                9:r.kBlue-3
            }
        pass

    return colors[idx % modulo]

def getCyclicMarker(idx, modulo=10, markers=None):
    """
    Returns a marker style based on modular division of an index
    See: https://root.cern.ch/doc/master/classTAttMarker.html#M2

    idx     - current index

    modulo - base for modular division, e.g. idx % modulo
    """

    return (20 + (idx % modulo) )

def plotObservable(**kwargs):
    """
    Makes a plot comparing a given observable (obsName) from a class of observable 
    types (obsType) for a given particle species (particleName)


    Plotting modes:
        1. Compare across sel levels inside a single file
        2. Compare between gen and reco inside a single file
        3. Compare observable across two or more files

    Mandatory input arguments:

        dictOfInputFiles    - dictionary of input TFiles to be processed
                              Key is the physical filename and value is 
                              a legend entry.  If len is 1 the legend
                              entry will not be used.  If "data", or 
                              a case-insensitive variant, is in any of
                              the legend entries the output canvas name 
                              will be appended with "data"
        
        obsName             - Name of observable, see the lists stored 
                              in supObservables
        
        obsType             - Name of observable type, see keys of 
                              supObservables
        
        particleName        - Name of the particle, see supParticleNames 
                              for possible values

    Optional input arguments that control the plotting mode:

        selLvlReco          - Specific sel level to use for reco 
                              level plots, if not provided all levels in 
                              selLevels will be used.

        selLvlGen           - Specific sel level to use for gen level
                              plots, if not provided gen plots will not
                              be plotted
       
    Additional optional input arguments

        drawLeg             - draws the legend on the plot

        outFileName         - Physical filename of output TFile, if not 
                              provided one will be created

        outFileOption       - Option for making the output TFile, e.g.
                              from set {RECREATE,UPDATE,etc...}

        saveImage           - Saves a *.png and a *.C file of the plot

        setLogY             - Sets y-axis to be logarithmic
    """

    from LFVAnalysis.LFVUtilities.nesteddict import nesteddict
    from LFVAnalysis.LFVUtilities.utilities import selLevels, supObservables, supParticleNames
    from LFVAnalysis.LFVUtilities.wrappers import runCommand

    import os
    import ROOT as r

    # Set the batch mode
    r.gROOT.SetBatch(True)

    # Define the mc level
    mcLevels = ["reco"] # default for both mc and data

    #################################################
    # Get mandatory input arguments
    #################################################
    dictOfInputFiles= kwargs["dictOfInputFiles"]
    obsName         = kwargs["obsName"]
    obsType         = kwargs["obsType"]
    particleName    = kwargs["particleName"]
    
    if obsType not in supObservables.keys():
        print("plotObservable() - Usage Error:")
        print("\tThe obsType '%s' is not understood."%(obsType))
        print("\tPlease choose from the following list:")
        print("")
        print("\t",supObservables.keys())
        print("")
        print("Exiting")
        exit(os.EX_USAGE)
        pass

    if obsName not in supObservables[obsType]:
        print("plotObservable() - Usage Error:")
        print("\tThe obsName '%s' of type '%s' is not understood."%(obsName,obsType))
        print("\tPlease choose from the following list for this type:")
        print("")
        print("\t",supObservables[obsType])
        print("")
        print("Exiting")
        exit(os.EX_USAGE)
        pass

    if particleName not in supParticleNames:
        print("plotObservable() - Usage Error:")
        print("\tThe particleName '%s' is not understood."%(particleName))
        print("\tPlease choose from the following list for this type:")
        print("")
        print("\t",particleName)
        print("")
        print("Exiting")
        exit(os.EX_USAGE)
        pass

    #################################################
    # Get optional arguments
    #################################################
    drawLeg = False
    if "drawLeg" in kwargs:
        drawLeg = kwargs["drawLeg"]
        pass
    
    outFileName = None
    if "outFileName" in kwargs:
        outFileName = kwargs["outFileName"]
        if "outFileOption" in kwargs:
            outFileOption = kwargs["outFileOption"]
        else:
            outFileOption = "RECREATE"

    setLogY = False
    if "setLogY" in kwargs:
        setLogY = kwargs["setLogY"]
        pass

    selLvlReco = None
    if "selLvlReco" in kwargs:
        selLvlReco = kwargs["selLvlReco"]
        pass

    selLvlGen = None
    if "selLvlGen" not in kwargs
        selLvlGen = kwargs["selLvlGen"]
        mcLevels.append("gen")
        pass

    #################################################
    # Check if operational mode is understood
    #################################################
    plotMode = -1
    if ( 
            (len(dictOfInputFiles) > 1) and (
                (selLvlReco is not None and selLvlGen is None) or
                (selLvlReco is None and selLvlGen is not None)
            )
       ):
        plotMode = 3
    elif (
            len(dictOfInputFiles) == 1 and
            selLvlReco is not None and
            selLvlGen is not None
         ):
        plotMode = 2
    elif (
            len(dictOfInputFiles) == 1 and
            selLvlReco is None and
            selLvlGen is None
         ):
        plotMode = 1
    else:
        print("plotObservable() - Usage Error:")
        print("\tUnable to determine the operating mode, possible modes are:")
        print("\t\t1. One input File and neither selLvlReco or selLvlGen supplied")
        print("\t\t2. One input File and both selLvlReco and selLvlGen supplied")
        print("\t\t3. Multiple input Files and either selLvlReco or selLvlGen supplied")
        print("Exiting")
        exit(os.EX_USAGE)
        pass

    #################################################
    # Get All Plots
    #################################################
    r.TH1.AddDirectory(False) # Input File does not manage TH1 Objets

    thereIsData = False
    dictOfPlots = nesteddict() # dictOfPlots[selLvl][mcLvl] = (Plot, legEntry)
    for filename,legEntry in dictOfInputFiles.iteritems():
        try:
            thisFile = r.TFile(filename,"READ")
        except Exception as e:
            print("exception occured when trying to open file: '%s'"%(filename))
            print("exception: ", e)
            exit(os.EX_DATAERR)
        if thisFile.IsZombie():
            print("error: zombie file encountered, file: '%s'"%s(filename))
            print("Exiting")
            exit(os.EX_DATAERR)

        if "data" in legEntry.lower():
            thereIsData = True

        # Load the plot
        if plotMode == 1:
            for selLvl in selLevels:
                # Name as: h_<mcLvl>_<particleName>_<obsName>_<selLvl>
                histoName = "h_%s_%s_%s_%s"%(mcLevels[0],particleName,obsName,selLvl)
                
                # Path as: particleName/selLvl/obsType/mcLvl/histoName
                histoPath = "%s/%s/%s/%s/%s"%(particleName,selLvl,obsType,mcLevels[0],histoName)
                
                # Get the plot
                dictOfPlots[selLvl][mcLevels[0]] = (
                        thisFile.Get(histoPath),
                        selLvl
                        )
                pass # end loop over selLevels
            pass # end plotMode == 1
        elif plotMode == 2:
            # Get the reco level plot
            # Name as: h_<mcLvl>_<particleName>_<obsName>_<selLvl>
            histoName = "h_%s_%s_%s_%s"%(mcLevels[0],particleName,obsName,selLvlReco)
            
            # Path as: particleName/selLvl/obsType/mcLvl/histoName
            histoPath = "%s/%s/%s/%s/%s"%(particleName,selLvlReco,obsType,mcLevels[0],histoName)
            
            # Get the plot
            dictOfPlots[selLvl][mcLevels[0]] = (
                    thisFile.Get(histoPath),
                    "%s: %s"%(mcLevels[0], selLvlReco)
                    )

            # Get the gen level plot
            # Name as: h_<mcLvl>_<particleName>_<obsName>_<selLvl>
            histoName = "h_%s_%s_%s_%s"%(mcLevels[1],particleName,obsName,selLvlReco)
            
            # Path as: particleName/selLvl/obsType/mcLvl/histoName
            histoPath = "%s/%s/%s/%s/%s"%(particleName,selLvlReco,obsType,mcLevels[1],histoName)
            
            # Get the plot
            dictOfPlots[selLvl][mcLevels[1]] = (
                    thisFile.Get(histoPath),
                    "%s: %s"%(mcLevels[1], selLvlReco)
                    )
            pass # end plotMode == 2
        elif plotMode == 3:
            # Determine the selLevel
            if (selLvlReco is not None and selLvlGen is None):
                selLvl = selLvlReco
                mcLvl = mcLevels[0]
            elif (selLvlReco is None and selLvlGen is not None):
                selLvl = selLvlGen
                mcLvl = mcLevels[1]
                pass

            # Get the plot
            # Name as: h_<mcLvl>_<particleName>_<obsName>_<selLvl>
            histoName = "h_%s_%s_%s_%s"%(mcLvl,particleName,obsName,selLvl)
            
            # Path as: particleName/selLvl/obsType/mcLvl/histoName
            histoPath = "%s/%s/%s/%s/%s"%(particleName,selLvl,obsType,mcLvl,histoName)
            
            # Get the plot
            dictOfPlots[selLvl][mcLvl] = (
                    thisFile.Get(histoPath),
                    "%s: %s - %s"%(legEntry, mcLvl, selLvl)
                    )
            pass # end plotMode == 3

        thisFile.Close()
        pass # end loop over dictOfInputFiles

    #################################################
    # Make the canvas
    #################################################
    # Make the name and title of the canvas
    # Name as canv_<particleName>_<obsName>_<canvAppend>
    if plotMode == 1:
        canvAppend = "compAllSelLvls"
    elif plotMode == 2:
        canvAppend = "compGen2Reco"
    elif plotMode == 3:
        canvAppend = "multiFile"
        pass

    canvName = "canv_%s_%s_%s"%(particleName, obsName, canvAppend)
    canvTitle = "%s: %s %s"%(particleName, obsName, canvAppend)
    
    if thereIsData:
        canvName += "_data"
        canvTitle += " data"
        pass
    
    obsCanvas = r.TCanvas(canvName, canvTitle, 600, 600)
    obsCanvas.cd()
    if setLogY:
        obsCanvas.cd().SetLogy()
        pass

    # Draw all plots
    plotLegend = r.Legend(0.5,0.6,0.9,0.9)
    for idx,selLvl in enumerate(dictOfPlots.keys()):
        for mcLvl,plotTuple in dictOfPlots[selLevels].iteritems():
            if idx == 0:
                drawOpt = "E1"
            else:
                drawOpt = "sameE1"
                pass

            # Set the style
            plotTuple[0].SetLineColor(getCyclicColor(idx))
            plotTuple[0].SetLineWidth(2)
            plotTuple[0].SetMarkerColor(getCyclicColor(idx))
            plotTuple[0].SetMarkerSize(0.8)
            plotTuple[0].SetMarkerStyle(20+idx)

            # Add to the legend
            plotLegend.AddEntry(plotTuple[0], plotTuple[1],"LPE")
            
            # Draw
            plotTuple[0].Draw(drawOpt)
            pass # end loop over inner dict
        pass # end loop over outer dict

    if drawLeg:
        plotLegend.Draw("same")
        pass

    if saveImage:
        plotDirName = outFileName.strip(".root")
        plotDirCmd = ['mkdir', '-p', plotDirName]
        runCommand(plotDirName)

        obsCanvas.SaveAs("%s/%s.png"%(plotDirName,canvName))
        obsCanvas.SaveAs("%s/%s.C"%(plotDirName,canvName))
        pass

    #################################################
    # Store the output?
    #################################################
    if outFileName is not None:
        try: 
            outFile = r.TFile(outFileName,outFileOption)
        except Exception as e:
            print "exception occured when trying to write '%s'"%(outFileName)
            print "maybe the output directory is not writeable?"
            print "exception: ", e
            exit(os.EX_DATAERR)
    
        # Make directory structure
        outFile.mkdir(particleName)
        dirParticle = outFile.GetDirectory(particleName)

        dirParticle.mkdir(obsType)
        dirObsType = dirParticle.GetDirectory(obsType)
        
        dirObsType.mkdir(obsName)
        dirObsName = dirObsType.GetDirectory(obsName)

        dirObsName.cd()
        obsCanvas.Write()
        pass

    return 0
