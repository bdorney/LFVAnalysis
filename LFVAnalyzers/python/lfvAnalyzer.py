from LFVAnalysis.LFVHistograms.ElHistos import ElHistos
from LFVAnalysis.LFVHistograms.HvyResHistos import HvyResHistos
from LFVAnalysis.LFVHistograms.MuonHistos import muonIdLabels, muonhitLabels, MuonHistos
from LFVAnalysis.LFVHistograms.PhysObjHistos import PhysObjHistos
from LFVAnalysis.LFVHistograms.TauHistos import TauHistos

from LFVAnalysis.LFVUtilities.nesteddict import nesteddict
from LFVAnalysis.LFVUtilities.selectorEl import getSelectedElectrons, elSelection
from LFVAnalysis.LFVUtilities.selectorMuon import getSelectedMuons, muonSelection 
from LFVAnalysis.LFVUtilities.selectorTau import getSelectedTaus, tauSelection 
from LFVAnalysis.LFVUtilities.utilities import selLevels, mcLevels

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
        self.isData = isData #whether input file is data or not
        self.anaGen = anaGen #analyze gen level information
        self.anaReco = anaReco #analyze reco level information
        self.sigPdgId1 = 13 #Particle Id of Hvy Resonance Daughter 1
        self.sigPdgId2 = 15 #Particle Id of Hvy Resonance Daughter 2

        self.useGlobalMuonTrack = False

        # Make Histograms
        self.elHistos = {}
        self.muHistos = {}
        self.tauHistos = {}
        self.hvyResHistos = {}
        if isData:
            # Placeholder
            self.elHistos["reco"] = ElHistos()
            self.muHistos["reco"] = MuonHistos()
            self.tauHistos["reco"] = TauHistos()
            self.hvyResHistos["reco"] = HvyResHistos()
        else:
            for lvl in mcLevels:
                self.elHistos[lvl] = ElHistos(mcType=lvl)
                self.muHistos[lvl] = MuonHistos(mcType=lvl)
                self.tauHistos[lvl] = TauHistos(mcType=lvl)
                self.hvyResHistos[lvl] = HvyResHistos(mcType=lvl)

        return

    def analyze(self, listOfTriggers=None, printLvl=1000, numEvts=-1, printGenList=False, printTrigInfo=False):
        """
        Analyzes data stored in self.dataTree and prints the 
        number of processed events every printLvl number of events

        listOfTriggers - List of triggers to be checked for passing, a logic OR of
                         all triggers is performed.  If the OR evaluates to 1 then
                         the event is accepted for further analysis

        printGenList   - if true prints a table, in markdown format, of pdgId 
                         and 4-vectors of gen particles, if self.isData is False 
                         does nothing
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
            for lvl in selLevels:
                selectedEls[lvl] = getSelectedElectrons(event, elSelection[lvl], event.gsf_n, listOfBranchNames=listBNames)
            
            # Get selected muons
            selectedMuons = nesteddict()
            for lvl in selLevels:
                selectedMuons[lvl] = getSelectedMuons(event, muonSelection[lvl], event.mu_n, listOfBranchNames=listBNames, useGlobalTrack=self.useGlobalMuonTrack)

            # Get selected taus
            selectedTaus = nesteddict()
            for lvl in selLevels:
                selectedTaus[lvl] = getSelectedTaus(event, tauSelection[lvl], event.tau_n, listOfBranchNames=listBNames)

            # Fill Histograms - Gen Level
            ##################################################################################
            if not self.isData and self.anaGen:
                genMulti = nesteddict() # Container to track the multiplicity of different particle species
                for lvl in selLevels:
                    genMulti[lvl] = nesteddict()

                for pdgId,listOfParts in selectedGenParts.iteritems():
                    for genPart in listOfParts:
                     
                        # Determine Multiplicity
                        if abs(genPart.pdgId) in genMulti["all"].keys():
                            genMulti["all"][abs(genPart.pdgId)]+=1
                        else:
                            genMulti["all"][abs(genPart.pdgId)]=1

                        # Fill histograms: Electrons - Kinematics
                        if abs(genPart.pdgId) == 11:
                            self.elHistos["gen"].dict_histosKin["all"].charge.Fill(genPart.charge)
                            self.elHistos["gen"].dict_histosKin["all"].energy.Fill(genPart.E())
                            self.elHistos["gen"].dict_histosKin["all"].eta.Fill(genPart.eta())
                            self.elHistos["gen"].dict_histosKin["all"].mass.Fill(genPart.M())
                            self.elHistos["gen"].dict_histosKin["all"].pt.Fill(genPart.pt())
                    
                        # Fill histograms: Muons - Kinematics
                        if abs(genPart.pdgId) == 13:
                            self.muHistos["gen"].dict_histosKin["all"].charge.Fill(genPart.charge)
                            self.muHistos["gen"].dict_histosKin["all"].eta.Fill(genPart.eta())
                            self.muHistos["gen"].dict_histosKin["all"].mass.Fill(genPart.M())
                            self.muHistos["gen"].dict_histosKin["all"].pt.Fill(genPart.pt())
                        
                        # Fill histograms: Taus - Kinematics
                        if abs(genPart.pdgId) == 15:
                            self.tauHistos["gen"].dict_histosKin["all"].charge.Fill(genPart.charge)
                            self.tauHistos["gen"].dict_histosKin["all"].eta.Fill(genPart.eta())
                            self.tauHistos["gen"].dict_histosKin["all"].mass.Fill(genPart.M())
                            self.tauHistos["gen"].dict_histosKin["all"].pt.Fill(genPart.pt())

            # Fill Histograms - Reco Level
            ##################################################################################
            # Loop over electrons
            for lvl in selLevels:
                self.elHistos["reco"].dict_histosKin[lvl].multi.Fill(len(selectedEls[lvl])) # Multiplicity
                for el in selectedEls[lvl]:
                    self.elHistos["reco"].dict_histosKin[lvl].charge.Fill(el.charge)
                    self.elHistos["reco"].dict_histosKin[lvl].energy.Fill(el.E())
                    self.elHistos["reco"].dict_histosKin[lvl].eta.Fill(el.eta())
            
            # Loop over muons
            for lvl in selLevels:
                self.muHistos["reco"].dict_histosKin[lvl].multi.Fill(len(selectedMuons[lvl])) # Multiplicity
                for muon in selectedMuons[lvl]:
                    # Fill Kinematic Histos
                    self.muHistos["reco"].dict_histosKin[lvl].charge.Fill(muon.charge)
                    self.muHistos["reco"].dict_histosKin[lvl].eta.Fill(muon.eta())
                    self.muHistos["reco"].dict_histosKin[lvl].pt.Fill(muon.pt())
                    self.muHistos["reco"].dict_histosKin[lvl].pz.Fill(muon.pz())
                  
                    # Fill Id Histos
                    for binX,idLabel in enumerate(muonIdLabels):
                        if getattr(muon, idLabel) > 0:
                            self.muHistos["reco"].dict_histosId[lvl].idLabel.Fill(binX+1)
                            
                            for binY,hitLabel in enumerate(muonhitLabels):
                                self.muHistos["reco"].dict_histosId[lvl].dict_hitHistos[idLabel].Fill( getattr(muon, hitLabel), binY+1 )

                    self.muHistos["reco"].dict_histosId[lvl].dxy.Fill(muon.dxy)
                    self.muHistos["reco"].dict_histosId[lvl].dz.Fill(muon.dz)
                    self.muHistos["reco"].dict_histosId[lvl].normChi2.Fill(muon.normChi2)
                    
                    #Fill Iso Histos
                    self.muHistos["reco"].dict_histosIso[lvl].isoTrackerBased03.Fill(muon.isoTrackerBased03)

            # Loop over taus
            for lvl in selLevels:
                self.tauHistos["reco"].dict_histosKin[lvl].multi.Fill(len(selectedTaus[lvl])) # Multiplicity
                for tau in selectedTaus[lvl]:
                    self.tauHistos["reco"].dict_histosKin[lvl].charge.Fill(tau.charge)
                    self.tauHistos["reco"].dict_histosKin[lvl].eta.Fill(tau.eta())
                    self.tauHistos["reco"].dict_histosKin[lvl].mass.Fill(tau.M())
                    self.tauHistos["reco"].dict_histosKin[lvl].pt.Fill(tau.pt())
            
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
                    fourVec = dau1.fourVector + dau2.fourVector
                    if fourVec.M() > maxInvarMass:
                        maxInvarMass = fourVec.M()
                        candTuple = (dau1, dau2)

            fourVec = candTuple[0].fourVector + candTuple[1].fourVector
            hvyResCand = PhysObj(fourVec.Px(), fourVec.Py(), fourVec.Pz(), fourVec.E())
            hvyResCand.charge = candTuple[0].charge + candTuple[1].charge
            
            # Fill Reco level histos for hvy reso candidate - Kinematics
            self.hvyResHistos["reco"].dict_histosKin[selLevels[-1]].charge.Fill(hvyResCand.charge)
            self.hvyResHistos["reco"].dict_histosKin[selLevels[-1]].energy.Fill(hvyResCand.E())
            self.hvyResHistos["reco"].dict_histosKin[selLevels[-1]].eta.Fill(hvyResCand.eta())
            self.hvyResHistos["reco"].dict_histosKin[selLevels[-1]].mass.Fill(hvyResCand.M())
            self.hvyResHistos["reco"].dict_histosKin[selLevels[-1]].pt.Fill(hvyResCand.pt())

            if not self.isData and self.anaGen:
                candTupleGen = (selectedGenParts[self.sigPdgId1][0], selectedGenParts[self.sigPdgId2][0])
                fourVec = candTupleGen[0].fourVector + candTupleGen[1].fourVector
                hvyResCandGen = PhysObj(fourVec.Px(), fourVec.Py(), fourVec.Pz(), fourVec.E())
                hvyResCandGen.charge = candTupleGen[0].charge + candTupleGen[1].charge
                
                # Fill Reco level histos for hvy res candidate - Kinematics
                self.hvyResHistos["gen"].dict_histosKin[selLevels[-1]].charge.Fill(hvyResCandGen.charge)
                self.hvyResHistos["gen"].dict_histosKin[selLevels[-1]].energy.Fill(hvyResCandGen.E())
                self.hvyResHistos["gen"].dict_histosKin[selLevels[-1]].eta.Fill(hvyResCandGen.eta())
                self.hvyResHistos["gen"].dict_histosKin[selLevels[-1]].mass.Fill(hvyResCandGen.M())
                self.hvyResHistos["gen"].dict_histosKin[selLevels[-1]].pt.Fill(hvyResCandGen.pt())

                # Fill Mass Resolution Histograms for hvy res candidate
                self.hvyResHistos["reco"].dict_histosResol[selLevels[-1]].mass_response.Fill(hvyResCandGen.M(),hvyResCand.M())
                self.hvyResHistos["reco"].dict_histosResol[selLevels[-1]].massResol.Fill( (hvyResCand.M() - hvyResCandGen.M() ) / hvyResCandGen.M() )

                print "reco info:"
                print "| pdgId | status | charge | px | py | pz | E | pt | eta | mass |"
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

    def setAnalysisFlags(self, isData=False, anaGen=True, anaReco=True, sigPdgId1=13, sigPdgId2=15):
        """
        Sets the flags that control the behavior of a call of the analyze() method

        isData - perform data analysis
        anaGen - perform the gen particle analysis, note ignored if isData is True
        anaReco - performs the reco level analysis
        sigPdgId1 - particle id of hvy resonance daughter 1
        sigPdgId2 - particle id of hvy resonance daughter 2
        """

        self.isData = isData
        self.anaGen = anaGen
        self.anaReco = anaReco
        self.sigPdgId1 = sigPdgId1
        self.sigPdgId2 = sigPdgId2
        
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
