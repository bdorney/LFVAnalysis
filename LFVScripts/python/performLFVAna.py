#!/bin/env python

if __name__ == '__main__':
    from LFVAnalysis.LFVScripts.lfvOptions import parser
    parser.add_option("-i","--infilename", type="string", dest="inFile", default=None,
            help="input file to be analyzed", metavar="inFile")
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
    parser.set_defaults(
            isData=False,
            printGen=False,
            printTrig=False
            )
    (options, args) = parser.parse_args()
   
    # Check input file
    if options.inFile is None:
        print "no input file specified, exiting"
        exit(os.EX_USAGE)

    # Form list of triggers
    listOfTriggers = options.triggers.split(",")

    # Load macros
    import os
    import ROOT as r
    cmssw_base = os.getenv("CMSSW_BASE")
    r.gROOT.LoadMacro('%s/src/LFVAnalysis/LFVUtilities/include/getValFromVectorBool.h+'%cmssw_base)
    
    if options.debug:
        print "Input File:", options.inFile
        print "List of Triggers:", listOfTriggers
     
    from LFVAnalysis.LFVAnalyzers.lfvAnalyzer import lfvAnalyzer
    lfvAna = lfvAnalyzer(options.inFile)
    lfvAna.setAnalysisFlags(
            isData=options.isData, 
            anaGen=(not options.isData), 
            sigPdgId1=options.sigPdgId1, 
            sigPdgId2=options.sigPdgId2)

    # Externally defined selection?
    if options.selFileEl is not None:
        lfvAna.setAnalysisFlags(
                selFileEl=options.selFileEl
                )
        pass
    if options.selFileEvt is not None:
        lfvAna.setAnalysisFlags(
                selFileEvt=options.selFileEvt
                )
        pass
    if options.selFileMuon is not None:
        lfvAna.setAnalysisFlags(
                selFileMuon=options.selFileMuon
                )
        pass
    if options.selFileTau is not None:
        lfvAna.setAnalysisFlags(
                selFileTau=options.selFileTau
                )
        pass
    
    # analyze
    lfvAna.analyze(
            printLvl=options.printLvl, 
            listOfTriggers=listOfTriggers, 
            numEvts=options.numEvts, 
            printGenList=options.printGen,
            printTrigInfo=options.printTrig)
   
    # write output
    lfvAna.write(options.outFile,True)
