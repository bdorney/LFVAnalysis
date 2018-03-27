#!/bin/zsh

# Check for CMSSW_BASE
if [ -z "$CMSSW_BASE" ]
then
    echo "CMSSSW_BASE not set, please call cmsenv inside your CMSSW_X_Y_Z/src directory, e.g."
    echo ""
    echo "  cd CMSSW_<X>_<Y>_<Z>/src"
    echo "  cmsenv"
    echo ""
    echo "Then call this script again."
    return
fi

# Check if default virtualenv exists
VENV_BASE=$CMSSW_BASE/src/LFVAnalysis
if [ ! -d $VENV_BASE/default ]
then
    echo "Making default virtualenv, this may take some time"
    virtualenv $VENV_BASE/default -p python --system-site-packages
    pip install --upgrade pip
    pip install -U numpy root_numpy ipython
    #deactivate
else
    echo "Default virtualenv already exists, activating it"
    source $VENV_BASE/default/bin/activate
fi

echo "finished"
