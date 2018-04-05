#!/bin/env python

if __name__ == '__main__':
    # Get the path
    from LFVAnalysis.LFVUtilities.wrappers import envCheck
    envCheck('LFV_PATH')
    
    import os
    lfvPath = os.getenv('LFV_PATH')
    
    from LFVAnalysis.LFVUtilities.nesteddict import nesteddict
    dictOfObsFiles = nesteddict()

    # Setup baseline (e.g. kinematics)
    from LFVAnalysis.LFVUtilities.utilities import supObservables, supParticleNames
    for partName in supParticleNames:
        # open the file
        dictOfObsFiles[partName] = open("%s/Examples/listOfObservables_%s.txt"%(lfvPath,partName), 'w+')
        
        # automatic entry
        # write the kinematic observables
        dictOfObsFiles[partName].write('#particle name, observable type, observable name\n')
        for obs in supObservables["Kinematics"]:
            dictOfObsFiles[partName].write("%s,Kinematics,%s\n"%(partName,obs))
            pass # end writing kinematics

        # manual entrty - observables commont to all particles but not loopable
        if partName != "HvyRes":
            dictOfObsFiles[partName].write("%s,Identification,dxy\n"%(partName))
            dictOfObsFiles[partName].write("%s,Identification,dz\n"%(partName))
            dictOfObsFiles[partName].write("%s,Identification,idLabel\n"%(partName))
            dictOfObsFiles[partName].write("%s,Identification,normChi2\n"%(partName))
            pass

        # manual entry - specific observables to particle species
        if partName == "el":
            print "" # placeholder
        elif partName == "HvyRes":
            dictOfObsFiles[partName].write("%s,DaughterHistos,dR\n"%partName)
            dictOfObsFiles[partName].write("%s,MassResolution,massResol\n"%partName)
        elif partName == "mu":
            dictOfObsFiles[partName].write("%s,Isolation,isoTrkBased03\n"%partName)
        elif partName == "tau":
            dictOfObsFiles[partName].write("%s,Identification,againstElVLooseMVA6\n"%partName)
            dictOfObsFiles[partName].write("%s,Identification,againstMuonTight3\n"%partName)
            dictOfObsFiles[partName].write("%s,Identification,decayModeFinding\n"%partName)
            dictOfObsFiles[partName].write("%s,Isolation,tightIsoMVArun2v1DBoldBMwLT\n"%partName)

        # close the file
        dictOfObsFiles[partName].close()

        pass # end loop over particle name

    print("Observable files can be found in: \t%s/Examples"%lfvPath)
