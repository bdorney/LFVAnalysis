import os

cmssw_base = os.getenv("CMSSW_BASE")
inFile = "%s/test/RPV_MuTau_M_1800_LLE_LQD_Tree.root"%cmssw_base

import ROOT as r
r.gROOT.LoadMacro('%s/src/LFVAnalysis/LFVUtilities/include/getValFromVectorBool.h+'%cmssw_base)

from LFVAnalysis.LFVAnalyzers.lfvAnalyzer import lfvAnalyzer

listOfTriggers = [
            "trig_HLT_Mu50_accept",
            "trig_HLT_TkMu50_accept"
        ]

lfvAna = lfvAnalyzer(inFile, anaGen=True)
lfvAna.analyze(
        printLvl=1, 
        listOfTriggers=listOfTriggers, 
        #numEvts=-1, 
        numEvts=20, 
        printGenList=True,
        #printGenList=False,
        printTrigInfo=False)

lfvAna.write("output.root",True)
