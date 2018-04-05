#!/bin/env python

if __name__ == '__main__':
    import os
    
    from LFVAnalysis.LFVScripts.lfvOptions import parser
    parser.add_option("--cmssw",type="string",dest="cmssw_base", default="/user/dorney/CMSSW/CMSSW_8_0_17",
            help="physical file path for your $CMSSW_BASE directory",metavar="cmssw")
    parser.add_option("-i","--infilename", type="string", dest="inFile", default=None,
            help="input file containing TFiles files containing TTrees to be analyzed, one file per line", metavar="inFile")
    parser.add_option("-q","--queue", type="string", dest="queue", default="express",
            help="queue to submit your jobs to", metavar="queue")

    (options, args) = parser.parse_args()

    # Check if the queue is supported
    # See: http://doc.iihe.ac.be/wiki/t2b/index.php/Cluster_Overview#Queues
    supQueues = [ 'localgrid', 'highmem', 'highbw', 'express' ]
    if options.queue not in supQueues:
        print "queue '%s' not understood"%options.queue
        print "list of supported queues is:", supQueues
        exit(os.EX_USAGE)

    # Prepare the commands for making the
    from LFVAnalysis.LFVUtilities.wrappers import envCheck, runCommand
    envCheck('JOB_PATH')
    envCheck('LFV_PATH')

    import datetime
    startTime = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
    jobPath = "%s/%s"%(os.getenv('JOB_PATH'), startTime)
    setupCmds_JobPath = ["mkdir","-p", jobPath ]
    runCommand(setupCmds_JobPath)

    setupCmds_Link = ['ln','-sf',jobPath,'current'] #make a link for the most recent one
    runCommand(setupCmds_Link)

    outPath = "%s/rootfiles"%jobPath
    setupCmds_out = ["mkdir","-p", outPath ]
    runCommand(setupCmds_out)
    
    scriptPath = "%s/script"%jobPath
    setupCmds_script = ["mkdir","-p", scriptPath ]
    runCommand(setupCmds_script)

    stdOutPath = "%s/stdout"%jobPath
    setupCmds_stdout = ["mkdir","-p", stdOutPath ]
    runCommand(setupCmds_stdout)

    stdErrPath = "%s/stderr"%jobPath
    setupCmds_stderr = ["mkdir","-p", stdErrPath ]
    runCommand(setupCmds_stderr)

    # Open the Input File
    with open(options.inFile, 'r') as runs:
        runList = runs.readlines()

    # Strip new line character
    runList = [x.strip('\n') for x in runList]

    # Loop Over runs and launch a job for each of them
    for idx,run in enumerate(runList):
        parsedRunName = run.split('/')
        outFileName = ""
        for item in parsedRunName:
            if "crab" in item:
                outFileName += item
            elif ".root" in item:
                outFileName += "_%s"%item

        scriptName = outFileName.strip('.root')
        scriptName += '.sh'
        scriptName = "%s/%s"%(scriptPath, scriptName)
        
        scriptOut = outFileName.strip('.root')
        scriptOut += '.stdout'
        scriptOut = "%s/%s"%(stdOutPath, scriptOut)
        
        scriptErr = outFileName.strip('.root')
        scriptErr += '.stderr'
        scriptErr = "%s/%s"%(stdErrPath, scriptErr)

        outFileName = "%s/%s"%(outPath,outFileName)
        
        script = open(scriptName,'w+')
        script.write('#!/bin/bash\n')
        script.write('nodeDir=$PWD\n')
        script.write('source $VO_CMS_SW_DIR/cmsset_default.sh\n')
        script.write('cd %s/src\n'%options.cmssw_base)
        script.write('eval `scram runtime -sh`\n')
        script.write('source $CMSSW_BASE/src/LFVAnalysis/LFVScripts/setup/paths.sh\n')
        script.write('cd $nodeDir\n')
        
        #pythonCmd = 'python %s/src/LFVAnalysis/LFVScripts/python/performLFVAna.py -i%s -o%s --sigPdgId1=%i --sigPdgId2=%i'%(
        pythonCmd = 'performLFVAna.py -i%s -o%s --sigPdgId1=%i --sigPdgId2=%i --mindR=%f'%(
                run, 
                outFileName, 
                options.sigPdgId1, 
                options.sigPdgId2,
                options.mindR)
        pythonCmd += ' -t%s'%(options.triggers)
        if options.oppositeSign:
            pythonCmd += ' --oppositeSign'
        if options.debug:
            pythonCmd += ' --debug'
            print pythonCmd
        if options.selFileEl is not None:
            pythonCmd += ' --selFileEl=%s'%(options.selFileEl)
        if options.selFileMuon is not None:
            pythonCmd += ' --selFileMuon=%s'%(options.selFileMuon)
        if options.selFileTau is not None:
            pythonCmd += ' --selFileTau=%s'%(options.selFileTau)
        pythonCmd += '\n'

        script.write(pythonCmd)
        script.close()

        jobCmd = [ 
                'qsub',
                '-q',
                options.queue,
                '-o',
                scriptOut,
                '-e',
                scriptErr,
                scriptName ]

        if options.debug:
            print idx, jobCmd
        else:
            runCommand(jobCmd)    
    
    print "All Jobs Launched"
    print "To Check the status of your jobs:"
    print ""
    print "     qstat -u $USER"
    print ""
    print "Jobs can be stopped via the 'qdel' command"
