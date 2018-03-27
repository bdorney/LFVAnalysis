#!/bin/env python

if __name__ == '__main__':
    from optparse import OptionGroup, OptionParser
    parser = OptionParser()
    parser.add_option("-i","--infilename", type="string", dest="inFile", default=None,
            help="input file containing TFiles files containing TTrees to be analyzed, one file per line", metavar="inFile")
    parser.add_option("-o","--outfilename", type="string", dest="outFile", default-"lvfMassFitterOutput.root",
            help="output file name containing fit results", metavar="outFile")
    (options, args) = parser.parse_args()

    # Check if input file has been supplied
    import os
    if options.inFile is None:
        print "You must supply an input file via the '--infilename' option"
        exit(os.EX_USAGE)

    # Open the Input File
    try:
        with open(options.inFile, 'r') as runs:
            runList = runs.readlines()
    except Exception as e:
        print "exception occured when trying to open file: '%s'"%(options.inFile)
        print "exception: ", e
        exit(os.EX_DATAERR)

    # Strip new line character
    runList = [x.strip('\n') for x in runList]

    # Make the output file
    import ROOT as r
    try: 
        outFile = r.TFile(options.outFile,"RECREATE")
    except Exception as e:
        print "exception occured when trying to write '%s'"%(options.outFile)
        print "maybe the output directory is not writeable?"
        print "exception: ", e
        exit(os.EX_DATAERR)

    # Set the batch mode
    r.gROOT.SetBatch(True)

    # Make containers for fitting
    from LFVAnalysis.LFVUtilities.nesteddict import nesteddict
    dict_massFits = nesteddict()            # Fit
    dict_massResolHistos = nesteddict()     # Resolution
    dict_massResidualHistos = nesteddict()  # Residual (hResolution - Fit)

    list_dtypesTuple = [
            ('mass','f4'), 
            ('mass_err','f4'), 
            ('alpha','f4'), 
            ('N','f4'), 
            ('sigma','f4'), 
            ('mean','f4'), 
            ('normChi2','f4')
            ]
    import numpy as np
    array_fitRes = np.zeros(len(runList), dtype=list_dtypesTuple)

    # Loop over runs and fit a histogram for each of them
    from LFVAnalysis.LFVUtilities.utilities import selLevels
    for idx,run in enumerate(runList):
        # open the ROOT File
        try:
            dataFile = r.TFile(run,"READ")
        except Exception as e:
            print "exception occured when trying to read input TFile '%s'"%(run)
            print "exception: ", e

        # Determine the sample mass point
        hHvyResMass_Gen = dataFile.Get("HvyRes/%s/Kinematics/gen/h_gen_HvyRes_mass_%s"%(selLevels[-1],selLevels[-1]))
        array_fitRes[idx]['mass'] = hHvyResMass_Gen.GetMean(1)      # mean
        array_fitRes[idx]['mass_err'] = hHvyResMass_Gen.GetMean(11) # stdDev
        
        # Get the mass resolution histo
        dict_massResolHistos[array_fitRes[idx]['mass']] = dataFile.Get("HvyRes/%s/MassResolution/h_HvyRes_massResol_%s"%(selLevels[-1],selLevels[-1]))
        dict_massResolHistos[array_fitRes[idx]['mass']].SetName(
                "%s_m%i"%(
                    dict_massResolHistos[array_fitRes[idx]['mass']].GetName(),
                    int(mass[0])
                    )
                )

        # Initialize the mass residual histo
        dict_massResidualHistos[array_fitRes[idx]['mass']] = dict_massResolHistos[array_fitRes[idx]['mass']].Clone(
                    "h_HvyRes_massResol_residual_%s"%(selLevels[-1])
                )

        # Initialize the fit
        # p0 -> alpha
        # p1 -> N
        # p2 -> sigma
        # p3 -> mean
        dict_massFits[array_fitRes[idx]['mass']] = r.TF1(
                "func_hvyResMassFit_m%i"%(int(array_fitRes[idx]['mass'])),
                "crystalball",
                -2.5,2.5)

        # Set an initial guess
        dict_massFits[array_fitRes[idx]['mass']].SetParameter(2, dict_massResolHistos[array_fitRes[idx]['mass']].GetMean(1))
        dict_massFits[array_fitRes[idx]['mass']].SetParameter(3, dict_massResolHistos[array_fitRes[idx]['mass']].GetMean(11))

        # Perform the fit
        fitResult = dict_massResolHistos[array_fitRes[idx]['mass']].Fit(dict_massFits[array_fitRes[idx]['mass']],"SQ")
        fitValid = fitResult.IsValid()
        if not fitValid:
            continue
        
        # Store the output for summary plotting
        fit_chi2 = dict_massFits[array_fitRes[idx]['mass']].GetChisquare()
        fit_ndf = dict_massFits[array_fitRes[idx]['mass']].GetNDF()

        array_fitRes[idx]['alpha']      = dict_massFits[array_fitRes[idx]['mass']].GetParameter(0)
        array_fitRes[idx]['N']          = dict_massFits[array_fitRes[idx]['mass']].GetParameter(1)
        array_fitRes[idx]['sigma']      = dict_massFits[array_fitRes[idx]['mass']].GetParameter(2)
        array_fitRes[idx]['mean']       = dict_massFits[array_fitRes[idx]['mass']].GetParameter(3)
        array_fitRes[idx]['normChi2']   = fit_chi2 / fit_ndf
    
        # Make the residual distribution
        dict_massResidualHistos[array_fitRes[idx]['mass']].Add(dict_massFits[array_fitRes[idx]['mass']], -1.)

        # Store the output
        outFile.mkdir("m%i"%(int(array_fitRes[idx]['mass'])))
        dirMass = outFile.GetDirectory("m%i"%(int(array_fitRes[idx]['mass'])))
        dirMass.cd()
        dict_massFits[array_fitRes[idx]['mass']].Write()
        dict_massResolHistos[array_fitRes[idx]['mass']].Write()
        dict_massResidualHistos[array_fitRes[idx]['mass']].Write()
        pass

    # Make Summary Plot Directory
    outFile.mkdir("Summary")
    dirSummary = outFile.GetDirectory("Summary")
    dirSummary.cd()

    # Mass Resolution
    gMassRes = r.TGraphErrors(
            len(runList),
            array_fitRes['mass'],
            array_fitRes['mean'],
            array_fitRes['mass_err'],
            array_fitRes['sigma']
            )
    gMassRes.SetName("g_resol_vs_mass")
    gMassRes.Write()

    # Normalized Chi2
    gNormChi2 = r.TGraphErrors(
            len(runList),
            array_fitRes['mass'],
            array_fitRes['normChi2'],
            array_fitRes['mass_err'],
            np.zeros(len(runList))
            )
    gNormChi2.SetName("g_normChi2_vs_mass")
    gNormChi2.Write()
