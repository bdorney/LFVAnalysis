#!/bin/env python

if __name__ == '__main__':
    from optparse import OptionGroup, OptionParser
    parser = OptionParser()
    parser.add_option("-i","--infilename", type="string", dest="inFile", default=None,
            help="input file containing TFiles files containing TTrees to be analyzed, one file per line", metavar="inFile")
    parser.add_option("-o","--outfilename", type="string", dest="outFile", default="lfvMassFitterOutput.root",
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
            ('sigma_err','f4'), 
            ('mean','f4'), 
            ('mean_err','f4'), 
            ('normChi2','f4')
            ]
    import numpy as np
    array_fitRes = np.zeros(len(runList), dtype=list_dtypesTuple)

    # Loop over runs and fit a histogram for each of them
    from LFVAnalysis.LFVUtilities.utilities import selLevels
    for idx,run in enumerate(runList):
        # Skip commented lines
        if run[0] == "#":
            continue
        
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
        
        strMass = str(int(round(array_fitRes[idx]['mass'])))

        # Get the mass resolution histo
        dict_massResolHistos[array_fitRes[idx]['mass']] = dataFile.Get("HvyRes/%s/MassResolution/h_HvyRes_massResol_%s"%(selLevels[-1],selLevels[-1]))
        dict_massResolHistos[array_fitRes[idx]['mass']].SetName(
                "%s_m%s"%(
                    dict_massResolHistos[array_fitRes[idx]['mass']].GetName(),
                    strMass
                    )
                )
        dict_massResolHistos[array_fitRes[idx]['mass']].SetTitle("Mass: %s GeV"%(strMass))

        # Initialize the mass residual histo
        dict_massResidualHistos[array_fitRes[idx]['mass']] = dict_massResolHistos[array_fitRes[idx]['mass']].Clone(
                    "h_HvyRes_massResol_residual_%s"%(selLevels[-1])
                )

        # Determine the last nonzero bin
        lastNonZeroX = 1.0
        for binX in range(dict_massResolHistos[array_fitRes[idx]['mass']].GetNbinsX()+1,1,-1):
            if dict_massResolHistos[array_fitRes[idx]['mass']].GetBinContent(binX) > 0:
            #if dict_massResolHistos[array_fitRes[idx]['mass']].GetBinContent(binX) > 10:
                lastNonZeroX = dict_massResolHistos[array_fitRes[idx]['mass']].GetBinCenter(binX)
                break

        # Determine the first nonzero bin
        firstNonZeroX = -1.0
        for binX in range(1,dict_massResolHistos[array_fitRes[idx]['mass']].GetNbinsX()+1):
            if dict_massResolHistos[array_fitRes[idx]['mass']].GetBinContent(binX) > 0:
            #if dict_massResolHistos[array_fitRes[idx]['mass']].GetBinContent(binX) > 10:
                firstNonZeroX = dict_massResolHistos[array_fitRes[idx]['mass']].GetBinCenter(binX)
                break


        # Initialize the fit
        parNames = {       # For readability
                "constant":0,
                "mean":1,
                "sigma":2,
                "alpha":3,  # Transition point btw power-law & guassian
                "N":4       # exonent of power law
                }
        dict_massFits[array_fitRes[idx]['mass']] = r.TF1(
                "func_hvyResMassFit_m%s"%(strMass),
                "crystalball",
                firstNonZeroX,lastNonZeroX)

        # Set initial guess
        dict_massFits[array_fitRes[idx]['mass']].SetParameter(parNames["constant"], dict_massResolHistos[array_fitRes[idx]['mass']].GetMaximum())
        dict_massFits[array_fitRes[idx]['mass']].SetParameter(parNames["mean"],     dict_massResolHistos[array_fitRes[idx]['mass']].GetMean())
        dict_massFits[array_fitRes[idx]['mass']].SetParameter(parNames["sigma"],    dict_massResolHistos[array_fitRes[idx]['mass']].GetRMS())
        dict_massFits[array_fitRes[idx]['mass']].SetParameter(parNames["N"],        1)

        # Limit fit parameters
        #dict_massFits[array_fitRes[idx]['mass']].SetParLimits(3,-1e12,0.0)
        dict_massFits[array_fitRes[idx]['mass']].SetParLimits(3,firstNonZeroX,0.0)
        #dict_massFits[array_fitRes[idx]['mass']].SetParLimits(3,0.0, lastNonZeroX)
        #dict_massFits[array_fitRes[idx]['mass']].SetParLimits(3,firstNonZeroX,lastNonZeroX)
        dict_massFits[array_fitRes[idx]['mass']].SetParLimits(4,1e-12,1e12)

        # Perform the fit iteratively
        print "Fitting mass point: %f"%(array_fitRes[idx]['mass'])
        r.TVirtualFitter.SetMaxIterations(10000)
        fitResult = dict_massResolHistos[array_fitRes[idx]['mass']].Fit(dict_massFits[array_fitRes[idx]['mass']],"LLRSM")
        
        # Store the output for summary plotting
        fit_chi2 = dict_massFits[array_fitRes[idx]['mass']].GetChisquare()
        fit_ndf = dict_massFits[array_fitRes[idx]['mass']].GetNDF()

        array_fitRes[idx]['alpha']      = dict_massFits[array_fitRes[idx]['mass']].GetParameter(parNames['alpha'])
        array_fitRes[idx]['N']          = dict_massFits[array_fitRes[idx]['mass']].GetParameter(parNames['N'])
        array_fitRes[idx]['sigma']      = dict_massFits[array_fitRes[idx]['mass']].GetParameter(parNames['sigma'])
        array_fitRes[idx]['sigma_err']  = dict_massFits[array_fitRes[idx]['mass']].GetParError(parNames['sigma'])
        array_fitRes[idx]['mean']       = dict_massFits[array_fitRes[idx]['mass']].GetParameter(parNames['mean'])
        array_fitRes[idx]['mean_err']   = dict_massFits[array_fitRes[idx]['mass']].GetParError(parNames['mean'])
        array_fitRes[idx]['normChi2']   = fit_chi2 / fit_ndf
    
        # Make the residual distribution
        dict_massResidualHistos[array_fitRes[idx]['mass']].Add(dict_massFits[array_fitRes[idx]['mass']], -1.)

        # Store the output
        outFile.mkdir("m%s"%(strMass))
        dirMass = outFile.GetDirectory("m%s"%(strMass))
        dirMass.cd()
        dict_massFits[array_fitRes[idx]['mass']].Write()
        dict_massResolHistos[array_fitRes[idx]['mass']].Write()
        dict_massResidualHistos[array_fitRes[idx]['mass']].Write()
        
        canvName = run.strip(".root")
        canvName = "%s_massResolution_m%s"%(canvName, strMass)
        canv_MassRes = r.TCanvas(canvName,"Mass Resolution - %s GeV"%(strMass), 600, 600)
        canv_MassRes.Draw()
        canv_MassRes.cd().SetLogy()
        dict_massResolHistos[array_fitRes[idx]['mass']].Draw("E1")
        canv_MassRes.SaveAs("%s.png"%(canvName))

        pass

    # Make Summary Plot Directory
    print "Fitting Finished, Storing Summary Output"
    outFile.mkdir("Summary")
    dirSummary = outFile.GetDirectory("Summary")
    dirSummary.cd()

    gMassRes = r.TGraphErrors(len(runList))
    gNormChi2 = r.TGraphErrors(len(runList))
    
    gMassRes.SetName("g_resol_vs_mass")
    gNormChi2.SetName("g_normChi2_vs_mass")
    
    for idx, run in enumerate(runList):
        gMassRes.SetPoint(idx, array_fitRes[idx]['mass'], array_fitRes[idx]['sigma'])
        gMassRes.SetPointError(idx, array_fitRes[idx]['mass_err'], array_fitRes[idx]['sigma_err'])
        
        gNormChi2.SetPoint(idx, array_fitRes[idx]['mass'], array_fitRes[idx]['normChi2'])
        gNormChi2.SetPointError(idx, array_fitRes[idx]['mass_err'], 0.)
        
        pass
    
    gMassRes.Write()
    gNormChi2.Write()

    # Close Output File
    outFile.Close()

    print "Completed"
