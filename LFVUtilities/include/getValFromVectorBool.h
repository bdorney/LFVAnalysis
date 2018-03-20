
#ifndef __LFVUTILTIES_getValFromVectorBool__
#define __LFVUTILTIES_getValFromVectorBool__

#include <stdio.h>
#include <vector>

bool getValFromVectorBool(const std::vector<bool> vec, const int index) {
      if (vec[index]) return true;
      else return false;
} //End getValFromVectorBool()

#endif
