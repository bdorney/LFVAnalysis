from LFVAnalysis.LFVHistograms.ElHistos import elIdLabels, ElHistos
from LFVAnalysis.LFVHistograms.HvyResHistos import HvyResHistos
from LFVAnalysis.LFVHistograms.MuonHistos import muonIdLabels, muonhitLabels, MuonHistos
from LFVAnalysis.LFVHistograms.PhysObjHistos import PhysObjHistos
from LFVAnalysis.LFVHistograms.TauHistos import tauIdLabels, TauHistos

from LFVAnalysis.LFVUtilities.nesteddict import nesteddict
from LFVAnalysis.LFVUtilities.selectorEl import getSelectedElectrons, elSelection
from LFVAnalysis.LFVUtilities.selectorMuon import getSelectedMuons, muonSelection 
from LFVAnalysis.LFVUtilities.selectorTau import getSelectedTaus, tauSelection 
from LFVAnalysis.LFVUtilities.utilities import dR, fillKinematicHistos, selLevels, mcLevels

from LFVAnalysis.LFVObjects.physicsObject import *

import os
import ROOT as r

class lfvAnalyzer:
    def __init__(self, inputFileName, inputTreeName="IIHEAnalysis", isData=False, anaGen=True, anaReco=True):
        """
        inputFileName - physical filename of input TFile to perform analysis on
        inputTreeName - name of TTree found in inputFileName
        isData - True (False) if running over data (MC)
        anaGen - Set to true if generator level analysis is desired
        anaReco - Set to true if reco level analysis is desired
        """

        # Get Input TTree
        self.inputFileName = inputFileName #store this for later
        try:
            self.dataFile = r.TFile(inputFileName, "READ", "", 1)
            self.dataTree = self.dataFile.Get(inputTreeName)
        except Exception as e:
            print "exception occured when trying to retrive TTree %s from TFile %s"%(inputTreeName,inputFileName)
            print "exception: ", e
            exit(os.EX_DATAERR)

        # Analysis control flags
        # can be set via the setAnalysisFlags() method
        self.anaGen = anaGen                #analyze gen level information
        self.anaReco = anaReco              #analyze reco level information
        self.forceDaughterPairOS = False    #If True require lepton pair to be oppositely charged
        self.isData = isData                #whether input file is data or not
        self.minDaughterPairdR = -1.        #Minimum dR allowed between Hvy Res daughters
        self.sigPdgId1 = 13                 #Particle Id of Hvy Resonance Daughter 1
        self.sigPdgId2 = 15                 #Particle Id of Hvy Resonance Daughter 2
        self.useGlobalMuonTrack = False     #If True (False) use Global (IBT) muon track

        # Make Histograms
        self.elHistos = {}
        self.muHistos = {}
        self.tauHistos = {}
        self.hvyResHistos = {}
        if isData:
            # Placeholder
            self.elHistos["reco"] = ElHistos(mcType="reco")
            self.muHistos["reco"] = MuonHistos(mcType="reco")
            self.tauHistos["reco"] = TauHistos(mcType="reco")
            self.hvyResHistos["reco"] = HvyResHistos(mcType="reco")
        else:
            for mcLvl in mcLevels:
                self.elHistos[mcLvl] = ElHistos(mcType=mcLvl)
                self.muHistos[mcLvl] = MuonHistos(mcType=mcLvl)
                self.tauHistos[mcLvl] = TauHistos(mcType=mcLvl)
                self.hvyResHistos[mcLvl] = HvyResHistos(mcType=mcLvl)

        return

    def analyze(self, listOfTriggers=None, printLvl=1000, numEvts=-1, printGenList=False, printTrigInfo=False, printHvyResInfo=False):
        """
        Analyzes data stored in self.dataTree and prints the 
        number of processed events every printLvl number of events

        listOfTriggers - List of triggers to be checked for passing, a logic OR of
                         all triggers is performed.  If the OR evaluates to 1 then
                         the event is accepted for further analysis

        printGenList   - if true prints a table, in markdown format, of pdgId 
                         and 4-vectors of gen particles, if self.isData is False 
                         does nothing

        printHvyResInfo- if true prints a table, in markdown format, of info on
                         selected heavy resonance candidate at gen and reco level
        """

        # Tell the user which file we are analyzing
        print "analyzing input file: %s"%(self.inputFileName)

        # Loop over input TTree
        analyzedEvts = 0
        listBNames = [branch.GetName() for branch in self.dataTree.GetListOfBranches()]
        for event in self.dataTree:
            # Increment number of analyzed events
            analyzedEvts += 1

            # Exit if we've analyzed the requested number of events
            if numEvts > -1 and analyzedEvts > numEvts:
                break

            # Tell the user the number of analyzed events
            if (analyzedEvts % printLvl) == 0:
                print "Processed %i number of events"%analyzedEvts 

            ##################################################################################
            ##################################################################################
            # Trigger Selection
            ##################################################################################
            ##################################################################################
            if listOfTriggers is not None: # Allow the user the option to run w/o a trigger
                dict_trigInfo = {}
                if printTrigInfo:
                    print "| idx | trigName | Decision |"
                    print "| --- | -------- | -------- |"

                for idx,trigName in enumerate(listOfTriggers):
                    dict_trigInfo[trigName] = getattr(event, trigName)
                    if printTrigInfo:
                        print "| %i | %s | %i |"%(idx, trigName, dict_trigInfo[trigName])

                trigAccept = sum(dict_trigInfo.values())
                if printTrigInfo:
                    print "trigAccept = %i"%trigAccept

                if not (trigAccept > 0):
                    continue #None of the triggers passed, skip the event

                if printTrigInfo:
                    print "trigger selection passed"

            ##################################################################################
            ##################################################################################
            # Physics Object Selection
            ##################################################################################
            ##################################################################################
            
            # Select particles - Gen Level
            ##################################################################################
            selectedGenParts = nesteddict() # dictionary, keys -> pdgId, value -> list of genPart passing selection
            if not self.isData and self.anaGen:
                if printGenList:
                    print "| pdgId | status | px | py | pz | E | pt | eta | M |"
                    print "| ----- | ------ | -- | -- | -- | - | -- | --- | - |"
        
                for idx in range(0,event.mc_px.size()):
                    genPart = PhysObj(
                            event.mc_px.at(idx),
                            event.mc_py.at(idx),
                            event.mc_pz.at(idx),
                            event.mc_energy.at(idx),
                            event.mc_pdgId.at(idx),
                            event.mc_status.at(idx)
                            )
                    genPart.charge = event.mc_charge.at(idx)
            
                    if printGenList:
                        print "| %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                                genPart.pdgId, 
                                genPart.status, 
                                genPart.px(), 
                                genPart.py(), 
                                genPart.pz(), 
                                genPart.E(),
                                genPart.pt(),
                                genPart.eta(),
                                genPart.M())

                    if not ((abs(genPart.pdgId) == self.sigPdgId1) or (abs(genPart.pdgId) == self.sigPdgId2)):
                        continue
                    if genPart.status != 23:
                        continue

                    # Reaching here means genPart passed selection
                    if genPart.pdgId in selectedGenParts.keys():
                        selectedGenParts[abs(genPart.pdgId)].append(genPart)
                    else:
                        selectedGenParts[abs(genPart.pdgId)] = [ genPart ]

            # Select particles - Reco Level
            ##################################################################################
            # Get selected electrons
            selectedEls = nesteddict()
            for selLvl in selLevels:
                selectedEls[selLvl] = getSelectedElectrons(event, elSelection[selLvl], event.gsf_n, listOfBranchNames=listBNames)
            
            # Get selected muons
            selectedMuons = nesteddict()
            for selLvl in selLevels:
                selectedMuons[selLvl] = getSelectedMuons(event, muonSelection[selLvl], event.mu_n, listOfBranchNames=listBNames, useGlobalTrack=self.useGlobalMuonTrack)

            # Get selected taus
            selectedTaus = nesteddict()
            for selLvl in selLevels:
                selectedTaus[selLvl] = getSelectedTaus(event, tauSelection[selLvl], event.tau_n, listOfBranchNames=listBNames)

            # Fill Histograms - Gen Level
            ##################################################################################
            if not self.isData and self.anaGen:
                genMulti = nesteddict() # Container to track the multiplicity of different particle species
                for selLvl in selLevels:
                    genMulti[selLvl] = nesteddict()

                for pdgId,listOfParts in selectedGenParts.iteritems():
                    for genPart in listOfParts:
                     
                        # Determine Multiplicity
                        if abs(genPart.pdgId) in genMulti["all"].keys():
                            genMulti["all"][abs(genPart.pdgId)]+=1
                        else:
                            genMulti["all"][abs(genPart.pdgId)]=1

                        # Fill histograms: Electrons - Kinematics
                        if abs(genPart.pdgId) == 11:
                            fillKinematicHistos(genPart, self.elHistos["gen"].dict_histosKin["all"])

                        # Fill histograms: Muons - Kinematics
                        if abs(genPart.pdgId) == 13:
                            fillKinematicHistos(genPart, self.muHistos["gen"].dict_histosKin["all"])
                        
                        # Fill histograms: Taus - Kinematics
                        if abs(genPart.pdgId) == 15:
                            fillKinematicHistos(genPart, self.tauHistos["gen"].dict_histosKin["all"])

                # Fill gen multiplicity
                for pdgId,multi in genMulti["all"].iteritems():
                    if pdgId == 11: self.elHistos["gen"].dict_histosKin["all"].multi.Fill(multi)
                    if pdgId == 13: self.muHistos["gen"].dict_histosKin["all"].multi.Fill(multi)
                    if pdgId == 15: self.tauHistos["gen"].dict_histosKin["all"].multi.Fill(multi)

            # Fill Histograms - Reco Level
            ##################################################################################
            # Loop over electrons
            for selLvl in selLevels:
                self.elHistos["reco"].dict_histosKin[selLvl].multi.Fill(len(selectedEls[selLvl])) # Multiplicity
                for el in selectedEls[selLvl]:
                    # Fill Kinematic Histos
                    fillKinematicHistos(el, self.elHistos["reco"].dict_histosKin[selLvl])
                    
                    # Fill Id Histos
                    for binX,idLabel in enumerate(elIdLabels):
                        if getattr(el, idLabel) > 0:
                            self.elHistos["reco"].dict_histosId[selLvl].idLabel.Fill(binX+1)

            # Loop over muons
            for selLvl in selLevels:
                self.muHistos["reco"].dict_histosKin[selLvl].multi.Fill(len(selectedMuons[selLvl])) # Multiplicity
                for muon in selectedMuons[selLvl]:
                    # Fill Kinematic Histos
                    fillKinematicHistos(muon, self.muHistos["reco"].dict_histosKin[selLvl])
                  
                    # Fill Id Histos
                    for binX,idLabel in enumerate(muonIdLabels):
                        if getattr(muon, idLabel) > 0:
                            self.muHistos["reco"].dict_histosId[selLvl].idLabel.Fill(binX+1)
                            
                            for binY,hitLabel in enumerate(muonhitLabels):
                                self.muHistos["reco"].dict_histosId[selLvl].dict_hitHistos[idLabel].Fill( getattr(muon, hitLabel), binY+1 )

                    self.muHistos["reco"].dict_histosId[selLvl].dxy.Fill(muon.dxy)
                    self.muHistos["reco"].dict_histosId[selLvl].dz.Fill(muon.dz)
                    self.muHistos["reco"].dict_histosId[selLvl].normChi2.Fill(muon.normChi2)
                    
                    # Fill Iso Histos
                    self.muHistos["reco"].dict_histosIso[selLvl].isoTrackerBased03.Fill(muon.isoTrackerBased03)

            # Loop over taus
            for selLvl in selLevels:
                self.tauHistos["reco"].dict_histosKin[selLvl].multi.Fill(len(selectedTaus[selLvl])) # Multiplicity
                for tau in selectedTaus[selLvl]:
                    # Fill Kinematic Histos
                    fillKinematicHistos(tau, self.tauHistos["reco"].dict_histosKin[selLvl])
            
                    # Fill Id Histos
                    for binX,idLabel in enumerate(tauIdLabels):
                        if getattr(tau, idLabel) > 0:
                            self.tauHistos["reco"].dict_histosId[selLvl].idLabel.Fill(binX+1)
                    
                    self.tauHistos["reco"].dict_histosId[selLvl].dxy.Fill(tau.dxy)
                    self.tauHistos["reco"].dict_histosId[selLvl].againstElVLooseMVA6.Fill(tau.againstElectronVLooseMVA6)
                    self.tauHistos["reco"].dict_histosId[selLvl].againstMuonTight3.Fill(tau.againstMuonTight3)
                    self.tauHistos["reco"].dict_histosId[selLvl].decayModeFinding.Fill(tau.decayModeFinding)

                    # Fill Iso Histos
                    self.tauHistos["reco"].dict_histosIso[selLvl].tightIsoMVArun2v1DBoldDMwLT.Fill(tau.byTightIsolationMVArun2v1DBoldDMwLT)

            ##################################################################################
            ##################################################################################
            # Final Event Selection
            ##################################################################################
            ##################################################################################
            numSelEls  = len(selectedEls[selLevels[-1]])  # Number of selected electrons from the final stage of selection
            numSelMuons = len(selectedMuons[selLevels[-1]]) # Number of selected muons from the final stage of selection
            numSelTaus  = len(selectedTaus[selLevels[-1]])  # Number of selected taus from the final stage of selection
            selectedDauPart1 = [] # List of selected daughter particle 1
            selectedDauPart2 = [] # List of selected daughter particle 2
            if (self.sigPdgId1 == 13 and self.sigPdgId2 == 15) or (self.sigPdgId1 == 15 and self.sigPdgId2 == 13): # case: mu tau
                if not (numSelMuons > 0 and numSelTaus > 0):
                    continue
                selectedDauPart1 = selectedMuons[selLevels[-1]]
                selectedDauPart2 = selectedTaus[selLevels[-1]]
            elif (self.sigPdgId1 == 13 and self.sigPdgId2 == 11) or (self.sigPdgId1 == 11 and self.sigPdgId2 == 13): # case: e mu
                if not (numSelMuons > 0 and numSelEls > 0):
                    continue
                selectedDauPart1 = selectedEls[selLevels[-1]]
                selectedDauPart2 = selectedMuons[selLevels[-1]]
            elif (self.sigPdgId1 == 15 and self.sigPdgId2 == 11) or (self.sigPdgId1 == 11 and self.sigPdgId2 == 15): # case: e tau
                if not (numSelTaus > 0 and numSelEls > 0):
                    continue
                selectedDauPart1 = selectedEls[selLevels[-1]]
                selectedDauPart2 = selectedTaus[selLevels[-1]]
            else:
                print "input daughter particle pairing not understood"
                print "daughter pdgId pairing: (%i, %i)"%(self.sigPdgId1, self.sigPdgId2)
                print "allowed pairings:"
                print "     (11,13)"
                print "     (11,15)"
                print "     (15,13)"
                print "or their permutations"
                print "exiting"
                exit(os.EX_USAGE)
                
            ##################################################################################
            ##################################################################################
            # Make the candidate - Use the one with the highest invariant mass
            ##################################################################################
            ##################################################################################
            fourVec = r.TLorentzVector
            maxInvarMass = -1
            candTuple = ()
            for dau1 in selectedDauPart1:
                for dau2 in selectedDauPart2:
                    # Do we require daughter particles to be oppsitely charged?
                    if self.forceDaughterPairOS:
                        if (dau1.charge * dau2.charge) > 0:
                            continue

                    # Check angular separation between daughters
                    if dR(dau1, dau2) < self.minDaughterPairdR:
                        continue

                    # Construct four-vector and check if it has the highest invariant mass
                    fourVec = dau1.fourVector + dau2.fourVector
                    if fourVec.M() > maxInvarMass:
                        maxInvarMass = fourVec.M()
                        candTuple = (dau1, dau2)
                        pass
                    pass
                pass

            # Make sure we selected a candidate tuple
            if len(candTuple) != 2:
                continue

            fourVec = candTuple[0].fourVector + candTuple[1].fourVector
            hvyResCand = PhysObj(fourVec.Px(), fourVec.Py(), fourVec.Pz(), fourVec.E())
            hvyResCand.charge = candTuple[0].charge + candTuple[1].charge
            
            # Fill Reco level histos for hvy reso candidate - Kinematics
            fillKinematicHistos(hvyResCand, self.hvyResHistos["reco"].dict_histosKin[selLevels[-1]])

            # Fill Daughter Histos
            self.hvyResHistos["reco"].dict_dauHistos[selLevels[-1]].dR.Fill( dR(candTuple[0], candTuple[1]) )

            if not self.isData and self.anaGen:
                candTupleGen = (selectedGenParts[self.sigPdgId1][0], selectedGenParts[self.sigPdgId2][0])
                fourVec = candTupleGen[0].fourVector + candTupleGen[1].fourVector
                hvyResCandGen = PhysObj(fourVec.Px(), fourVec.Py(), fourVec.Pz(), fourVec.E())
                hvyResCandGen.charge = candTupleGen[0].charge + candTupleGen[1].charge
                
                # Fill Reco level histos for hvy res candidate - Kinematics
                fillKinematicHistos(hvyResCandGen, self.hvyResHistos["gen"].dict_histosKin[selLevels[-1]])

                # Fill Mass Resolution Histograms for hvy res candidate
                self.hvyResHistos["reco"].dict_histosResol[selLevels[-1]].mass_response.Fill(hvyResCandGen.M(),hvyResCand.M())
                self.hvyResHistos["reco"].dict_histosResol[selLevels[-1]].massResol.Fill( (hvyResCand.M() - hvyResCandGen.M() ) / hvyResCandGen.M() )

                if printHvyResInfo:
                    print "reco info:"
                    print "| pdgId | status | charge | px | py | pz | E | pt | eta | mass |"
                    print "| :---: | :----: | :----: | -- | -- | -- | - | -- | :-: | :--: |"
                    print "| %i | %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                            candTuple[0].pdgId, 
                            candTuple[0].status, 
                            candTuple[0].charge, 
                            candTuple[0].px(), 
                            candTuple[0].py(), 
                            candTuple[0].pz(), 
                            candTuple[0].E(), 
                            candTuple[0].pt(), 
                            candTuple[0].eta(), 
                            candTuple[0].M() )
                    print "| %i | %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                            candTuple[1].pdgId, 
                            candTuple[1].status, 
                            candTuple[1].charge, 
                            candTuple[1].px(), 
                            candTuple[1].py(), 
                            candTuple[1].pz(), 
                            candTuple[1].E(), 
                            candTuple[1].pt(), 
                            candTuple[1].eta(), 
                            candTuple[1].M() )
                    print "| %i | %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                            hvyResCand.pdgId, 
                            hvyResCand.status, 
                            hvyResCand.charge, 
                            hvyResCand.px(), 
                            hvyResCand.py(), 
                            hvyResCand.pz(), 
                            hvyResCand.E(), 
                            hvyResCand.pt(), 
                            hvyResCand.eta(), 
                            hvyResCand.M() )

                    print "gen info:"
                    print "| pdgId | status | charge | px | py | pz | E | pt | eta | mass |"
                    print "| :---: | :----: | :----: | -- | -- | -- | - | -- | :-: | :--: |"
                    print "| %i | %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                            candTupleGen[0].pdgId, 
                            candTupleGen[0].status, 
                            candTupleGen[0].charge, 
                            candTupleGen[0].px(), 
                            candTupleGen[0].py(), 
                            candTupleGen[0].pz(), 
                            candTupleGen[0].E(), 
                            candTupleGen[0].pt(), 
                            candTupleGen[0].eta(), 
                            candTupleGen[0].M() )
                    print "| %i | %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                            candTupleGen[1].pdgId, 
                            candTupleGen[1].status, 
                            candTupleGen[1].charge, 
                            candTupleGen[1].px(), 
                            candTupleGen[1].py(), 
                            candTupleGen[1].pz(), 
                            candTupleGen[1].E(), 
                            candTupleGen[1].pt(), 
                            candTupleGen[1].eta(), 
                            candTupleGen[1].M() )
                    print "| %i | %i | %i | %f | %f | %f | %f | %f | %f | %f |"%(
                            hvyResCandGen.pdgId, 
                            hvyResCandGen.status, 
                            hvyResCandGen.charge, 
                            hvyResCandGen.px(), 
                            hvyResCandGen.py(), 
                            hvyResCandGen.pz(), 
                            hvyResCandGen.E(), 
                            hvyResCandGen.pt(), 
                            hvyResCandGen.eta(), 
                            hvyResCandGen.M() )
        
        return

    def setAnalysisFlags(self, **kwargs):
        """
        Sets the flags that control the behavior of a call of the analyze() method

        The keyword is assumed to be the same as the variable name for simplicity

        isData - perform data analysis
        anaGen - perform the gen particle analysis, note ignored if isData is True
        anaReco - performs the reco level analysis
        sigPdgId1 - particle id of hvy resonance daughter 1
        sigPdgId2 - particle id of hvy resonance daughter 2
        """

        if "anaGen" in kwargs:
            self.anaGen = kwargs["anaGen"]
        if "anaReco" in kwargs:
            self.anaReco = kwargs["anaReco"]
        if "forceDaughterPairOS" in kwargs:
            self.forceDaughterPairOS = kwargs["forceDaughterPairOS"]
        if "isData" in kwargs:
            self.isData = kwargs["isData"]
        if "minDaughterPairdR" in kwargs:
            self.minDaughterPairdR = kwargs["minDaughterPairdR"] 
        if "sigPdgId1" in kwargs:
            self.sigPdgId1 = kwargs["sigPdgId1"]
        if "sigPdgId2" in kwargs:
            self.sigPdgId2 = kwargs["sigPdgId2"]
        if "useGlobalMuonTrack" in kwargs:
            self.useGlobalMuonTrack = kwargs["useGlobalMuonTrack"]
        
        return

    def write(self, outputFileName, debug=False):
        """
        Writes TObjects to outputFileName.
        The output TFile is deleted each time
        """
        
        option="RECREATE"

        if debug:
            print "saving electron histograms"
        for key,histos in self.elHistos.iteritems():
            # write histos
            histos.write(outputFileName, option)
            
            # after first iteration change the option from recreate to update
            if option == "RECREATE":
                option = "UPDATE"

        if debug:
            print "saving muon histograms"
        for key,histos in self.muHistos.iteritems():
            histos.write(outputFileName, option)

        if debug:
            print "saving tau histograms"
        for key,histos in self.tauHistos.iteritems():
            histos.write(outputFileName, option)

        #if not self.isData:
        #    if debug:
        #        print "saving gen particle histograms"
        #    for key,histos in self.GenPartHistos.iteritems():
        #        histos.write(outputFileName, option)

        if debug:
            print "saveing heavy resonance candidate histograms"
        for key,histos in self.hvyResHistos.iteritems():
            histos.write(outputFileName, option)

        return
