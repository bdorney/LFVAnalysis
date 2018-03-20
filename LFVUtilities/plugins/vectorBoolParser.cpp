#include "LFVAnalysis/LFVUtilities/include/vectorBoolParser.h"
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(pluginvectorBoolParser){
    //class_<lfvUtils::kVectorBool>("kVectorBool")
    //    .def(vector_indexing_suite<lfvUtils::kVectorBool>() );

    class_<lfvUtils::parseVectorBool>("parseVectorBool")
        .def("parse", &lfvUtils::parseVectorBool::parse)
    ;
}
