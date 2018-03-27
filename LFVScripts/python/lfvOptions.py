from optparse import OptionGroup, OptionParser
parser = OptionParser()

parser.add_option("-d","--debug", action="store_true", dest="debug",
        help="flag for printing debug information", metavar="debug")
parser.add_option("--isData", action="store_true", dest="isData",
        help="Specify if sample is Data; otherwise will be treated as MC", metavar="isData")
parser.add_option("-t","--triggers",type="string", dest="triggers", default="trig_HLT_Mu50_accept,trig_HLT_TkMu50_accept",
        help="List of triggers to be used", metavar="triggers")

# Define the daughter group
daughterGroup = OptionGroup(
        parser, 
        "Heavy Resonance Daughter Options",
        "Options which specify properties or selection specific to the daughter particles for the heavy resonance candidate")
daughterGroup.add_option("--mindR", type="float",dest="mindR",default=-1.0,
        help="Minimum allowed angular separation between daughter particles", metavar="mindR")
daughterGroup.add_option("--oppositeSign",action="store_true",dest="oppositeSign",
        help="Require the daughter leptons be oppositely charged", metavar="oppositeSign")
daughterGroup.add_option("--sigPdgId1", type="int", dest="sigPdgId1", default=13,
        help="PdgId of the first daughter of the heavy resonance candidate", metavar="sigPdgId1")
daughterGroup.add_option("--sigPdgId2", type="int", dest="sigPdgId2", default=15,
        help="PdgId of the second daughter of the heavy resonance candidate", metavar="sigPdgId2")
parser.add_option_group(daughterGroup)
