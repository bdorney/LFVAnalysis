#ifndef __LFVUTILTIES_vectorBoolParser__
#define __LFVUTILTIES_vectorBoolParser__

#include <stdio.h>
#include <vector>
#include <boost/python.hpp>

namespace lfvUtils{
    //typedef std::vector<bool> kVectorBool;

    struct parseVectorBool{
        bool parse(std::vector<bool> inputVec, int idx){
          if (inputVec[idx] == true){
              return true;
          }
          else{
              return false;
          }
        } //End parse()
    }; //End parseVectorBool
}

#endif
