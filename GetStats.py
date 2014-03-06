#!/usr/bin/python

import os
import sys
import igraph
from myutils import functionsGraphsDirectoryName
import split2k

import numpy as np

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
myExt = ".gml"
Koptions = [1,2,3] #,4,5

tracePrints = True

sourceNames = ['getftp',"quotearg_buffer_restyled","sub_4047A0"]
BaseDir = os.path.join("..","workset","cloneWars","ALL")
sourcesDir = os.path.join(BaseDir,"sources") 
targetsDir = os.path.join(BaseDir,"targets")


#import locale
#locale.setlocale(locale.LC_ALL, 'en_US')

import re

def comma_me(intAmount):
    amount = str(intAmount)
    orig = amount
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', amount)
    if orig == new:
        return new
    else:
        return comma_me(new)

def printInt(myInt):
    #return locale.format("%d",myInt,grouping=True)
    return comma_me(myInt)

def getStats(collection):
    if len(collection) == 0:
        return "EMPTY (len==0)" 
    else:
        return " Sum:[" + printInt(sum(collection)) + "],Min:[" + printInt(min(collection)) + "],Max:[" + printInt(max(collection)) + "],Avg:[" + printInt(np.mean(collection)) + "],STD:[" + printInt(np.std(collection)) + "]"

#target tracelets info - number of tracelets

print "Sources (paper targets)\n\n"



for sourceName in sourceNames:
    refGraph = igraph.read(os.path.join(sourcesDir,sourceName) + myExt)
    for k in Koptions:
        counter = 0
        for tracelet in split2k.ksplitGraphObject(k, refGraph , True):
            counter += 1
            
        print sourceName + ": K=" + str(k) + " , count = " + str(counter)    
        
print "\n\nTargets (paper references)\n\n"

dictK = {}
for k in Koptions:
    dictK[k] = {}
    for collectionName in ["traceletPerFunctionInfo","opcodePerTraceletInfo","opcodePerBasicBlock","callsPerBB","callsPerTrace"]:
        dictK[k][collectionName] = []

Degrees = {"VInDegree":[],"VOutDgree":[]}
BBInGraphs = []

for exeName in os.listdir(targetsDir):
    numberOfFunctionsInTarget = 0
    currentExeDir = os.path.join(targetsDir,os.path.join(exeName,functionsGraphsDirectoryName))

    for funcFileName in filter(lambda x:x.endswith(myExt),os.listdir(currentExeDir)):
        
        tarGraph = igraph.read(os.path.join(currentExeDir,funcFileName))
        
        BBInGraphs.append(len(tarGraph.vs))
        
        continue
        
        for v in tarGraph.vs:
            Degrees['VInDegree'].append(v.indegree())
            Degrees['VOutDgree'].append(v.outdegree())
        
        for k in Koptions:
            
            traceletPerFunction  = 0
            dictUsed = dictK[k]

            for tracelet in split2k.ksplitGraphObject(k, tarGraph , True):
                traceletPerFunction +=1
                BB = []
                callsBB = []
                
                for v in tracelet.vs:
                    opcodesInBB = v['code'].count(";")
                    BB.append(opcodesInBB)
                    dictUsed['opcodePerBasicBlock'].append(opcodesInBB)
                    callsInBB = v['code'].count("call ")
                    callsBB.append(callsInBB)
                    dictUsed['callsPerBB'].append(callsInBB)
                    
                dictUsed['opcodePerTraceletInfo'].append(sum(BB))
                dictUsed['callsPerTrace'].append(sum(callsBB))
                
            dictUsed['traceletPerFunctionInfo'].append(traceletPerFunction)
      
      
print "BBInGraphs" +":",
print getStats(BBInGraphs)
    
return 
             
for k in Koptions:
    print "Data for K=" + str(k)
    dictUsed = dictK[k]
    for collectionName in ["traceletPerFunctionInfo","opcodePerTraceletInfo","opcodePerBasicBlock","callsPerBB","callsPerTrace"]:
        print collectionName +":",
        print getStats(dictUsed[collectionName])


for key in Degrees.keys():
    print key +":",
    print getStats(Degrees[key])
