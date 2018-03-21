#!/bin/env python

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
   
    parser.add_option("-d","--debug", action="store_true", dest="debug",
            help="flag for printing debug information", metavar="debug")
    parser.add_option("-i","--infilename", type="string", dest="inFile", default=None,
            help="input file to be analyzed", metavar="inFile")
    parser.add_option("--isData", action="store_true", dest="isData",
            help="Specify if sample is Data; otherwise will be treated as MC", metavar="isData")
    parser.add_option("-n","--numEvts", type="int", dest="numEvts", default=-1,
            help="Number of events to analyze, -1 results in all events", metavar="numEvts")
    parser.add_option("-o","--outfilename", type="string", dest="outFile", default="lfvOutput.root",
            help="Name of output TFile", metavar="outFile")
    parser.add_option("--printGen", action="store_true", dest="printGen",
            help="Prints a table of all gen particles for each event", metavar="printGen")
    parser.add_option("--printLvl", type="int", dest="printLvl", default=100,
            help="Prints a processing statement after this number of events", metavar="printLvl")
    parser.add_option("--printTrig",action="store_true", dest="printTrig",
            help="For each event print the trigger decision", metavar="printTrig")
    parser.add_option("--sigPdgId1", type="int", dest="sigPdgId1", default=13,
            help="PdgId of the first daughter of the heavy resonance candidate", metavar="sigPdgId1")
    parser.add_option("--sigPdgId2", type="int", dest="sigPdgId2", default=15,
            help="PdgId of the second daughter of the heavy resonance candidate", metavar="sigPdgId2")
    parser.add_option("-t","--triggers",action="append", dest="listOfTriggers", default=["trig_HLT_Mu50_accept","trig_HLT_TkMu50_accept"],
            help="List of triggers to be used", metavar="listOfTriggers")
    parser.set_defaults(
            isData=False,
            printGen=False,
            printTrig=False
            )
    (options, args) = parser.parse_args()

    import os
    cmssw_base = os.getenv("CMSSW_BASE")
    #inFile = "%s/test/RPV_MuTau_M_1800_LLE_LQD_Tree.root"%cmssw_base
    #inFile = "/pnfs/iihe/cms/store/user/dbeghin/RPVresonantToMuTau_M-1000_LLE_LQD-001_TuneCUETP8M1_13TeV-calchep-pythia8/crab_RPVresonantToMuTau_M-1000_LLE_LQD-001/170410_133802/0000/outfile_1.root"
    
    if options.inFile is None:
        print "no input file specified, exiting"
        exit(os.EX_USAGE)

    import ROOT as r
    r.gROOT.LoadMacro('%s/src/LFVAnalysis/LFVUtilities/include/getValFromVectorBool.h+'%cmssw_base)
    
    if options.debug:
        print "Input File:", options.inFile
        print "List of Triggers:", options.listOfTriggers
     
    #listOfTriggers = [
    #            "trig_HLT_Mu50_accept",
    #            "trig_HLT_TkMu50_accept"
    #        ]

    from LFVAnalysis.LFVAnalyzers.lfvAnalyzer import lfvAnalyzer
    lfvAna = lfvAnalyzer(options.inFile)
    lfvAna.setAnalysisFlags(
            isData=options.isData, 
            anaGen=(not options.isData), 
            sigPdgId1=options.sigPdgId1, 
            sigPdgId2=options.sigPdgId2)
    
    # analyze
    lfvAna.analyze(
            printLvl=options.printLvl, 
            listOfTriggers=options.listOfTriggers, 
            numEvts=options.numEvts, 
            printGenList=options.printGen,
            printTrigInfo=options.printTrig)
   
    # write output
    lfvAna.write(options.outFile,True)
