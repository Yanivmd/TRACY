#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      user
#
# Created:     24/05/2013
# Copyright:   (c) user 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      user
#
# Created:     05/08/2012
# Copyright:   (c) user 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from igraph import *
#from combinatorics import *

import os
import sys

from difflib import *

import itertools

from myutils import *


#unlike the DIFF once, this returns a boolean not a grade (or grade dict)
def compareDisAsmCode(refCode,tarCode):
    if refCode == tarCode:
        return {'normal':100}
    else:
        return {'normal':0}

def getCompareMethods():
    yield compareDisAsmCode


def ngramsSplitFile(windowSize,delta,fileFullPath):

    if fileFullPath.find("_intel_") == -1:    # hack to not analyse intel functions...
        #print "current file is: " + infile

        f = open(fileFullPath,"r")

        commandsCollection = list()
        currentCommandIndex = 0

        for command in f.read().split(";"):
            
            menem = command.split(" ")[0]

            # the last is always empty
            if len(menem)>0:
                if (currentCommandIndex > (windowSize-1)):
                    commandsCollection.pop(0)
                    commandsCollection.append(menem + ";")
                    if (currentCommandIndex % delta ==0):
                        yield {'code':"".join(commandsCollection)}
                        #ProcessGraphFunc(dict(code=commandsCollection),infile,"ngram-" + str(currentCommandIndex-windowSize) + "-" + str(currentCommandIndex))
                else:
                    commandsCollection.append(menem + ";")
                currentCommandIndex+=1

        f.close()