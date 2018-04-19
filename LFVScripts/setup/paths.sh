#!/bin/zsh

#export JOB_PATH=<your path>
#if [ -z "$JOB_PATH" ]
#then
#    echo "JOB_PATH not set, please set JOB_PATH to the directory of your choice"
#    echo " (export JOB_PATH=<your_path>) and then rerun this script"
#    return
#fi

if [ -z "$CMSSW_BASE" ]
then
    echo "CMSSW_BASE not set, please setup the CMSSW env"
    echo " (cmsenv) and then rerun this script"
    return
fi

# Export project
export LFV_PATH=$CMSSW_BASE/src/LFVAnalysis

# Set python virtualenv
source $LFV_PATH/LFVScripts/setup/createVirtualEnv.sh

# Setup PATH
export PATH=$PATH:$CMSSW_BASE/src/LFVAnalysis/LFVScripts/python

# Make observable files
if [ ! -f $LFV_PATH/Examples/listOfObservables1D_mu.txt ]
then
    makeListOfObservables1D.py
fi

# Done
echo JOB_PATH $JOB_PATH
echo LFV_PATH $LFV_PATH

echo "setup complete"
