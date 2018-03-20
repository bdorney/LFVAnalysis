import ROOT as r

class isolationHistos:
    def __init__(self, physObj="mu", selLevel="all", mcType=None):
        """
        physObj - string specifying physics object type
        selLevel - string specifying the selection type
        mcType - string specifying Monte Carlo data tier, e.g. gen or reco
        """

        prefix = "h_data"
        if mcType is not None:
            prefix = "h_%s"%mcType

        return

    def write(self, directory):
        """
        directory - TDirectory histograms should be written too
        """
        
        directory.cd()

        # Write Histos

        return
