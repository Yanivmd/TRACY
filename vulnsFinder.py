#!/usr/bin/python

import os
import sys
import igraph
from  myutils import GradeSystemsInfo,borders,getDurationStr,CounterXlsReport,functionsGraphsDirectoryName
import split2k
import time
import itertools
import threading
import multiprocessing
import numpy
from GraphletsCompareMyNG import getMatchedCmdsWithGrade,compareDisAsmCode
#import csv
from collections import OrderedDict
#from array import array
#from GraphletRewritter import RWDict
from GraphletsConstraintsNG import GraphletsConstraints
from sendMail import sendMail
#from SortedCollection import KBest

#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

methodSystemName = "MONGOINTv1"
csvName = "VULNZ"
#TODO - shared mem used for sourcesList3K
myK = 3
timeOutInSecs = 60*60*myK # give them k hours to finish..
myExt = ".gml"

#KToKeep = 3


#"RW_contain","RW_ratio"
gradeSystemNames = ['contain','ratio',"Solver_contain","Solver_ratio"]

BaseDir = os.path.join("..","workset","vulns")

sourceName = 'quotearg_buffer_restyled'

sourcesDir = os.path.join(BaseDir,"sources") 
sourceFunctionName = sourceName + myExt
targetsDir = os.path.join(BaseDir,"targets")



def CreateResultsDict(ordered=False):
    def returnFieldNames():
        for field in ["exe","funcname","#objects","K","Trace","System","Generator","GradeSystem","TimeStr","TimeNumber"]:
            yield field
        for border in borders:
            yield "match-" + str(border)
    def retNone():
        while True:
            yield None
    if ordered:
        return OrderedDict(zip(returnFieldNames(),retNone()))
    else:
        return dict(zip(returnFieldNames(),retNone()))

def doOneFunctionFileRW(workerParams):
    
    #sourcesList3k = workerParams['sourcesList3k']
    #tarGraph = workerParams['tarGraph']
    #refGraph = workerParams['refGraph']
    #exeName = workerParams['exeName']
    #funcfilename = workerParams['funcFileName']
    
    
    Function = workerParams[0]
    sourcesList3k = workerParams[1]  
    #tarGraph = ?
    #refGraph = ?
    exeName =  Function['package'] + "[" + Function['elf_name'] + "]"
    funcfilename = Function['function_name']
    
    gradesCache = []
    
    timeout = [False,time.time()]
    def toggleTimeout():
        timeout[0] = True
    # wait 3 hours
    timeOutTimer = threading.Timer(timeOutInSecs,toggleTimeout)
    timeOutTimer.start()
    
    allFields = []
    
    #if len(refGraph.vs) > 3000:
    #    print "skipping cuz > 3000 - func=" + funcfilename + ",exe-" + exeName
    #    return allFields
    
    # startVal of hack - only take the last 2 confs with k=3 (trace = true OR false)
    
    #bestKSolverDeltas = KBest(KToKeep,lambda x: 100-x['delta'],lambda x:x['delta'])
    #bestKSolverBroken = KBest(KToKeep,lambda x: 1000-x['broken'],lambda x:x['broken'])
    GradeSystemsInfoInst = GradeSystemsInfo(sourcesList3k, gradeSystemNames)
    
    startForXlsRecord = time.time()
    
    #this cache could probebly get optimized
    
    
    
    
    """
    for refvIndex, refv in enumerate(refGraph.vs):
        gradesCache.append([])
        #gradesCache[refv['id']] = {}
        for tarvIndex, tarv in enumerate(tarGraph.vs):
            gradesDict = getMatchedCmdsWithGrade(refv['code'],tarv['code'])
            #for key in grade.keys():
            gradesCache[refvIndex].append(gradesDict)
            #gradesCache[refvIndex][tarvIndex] = grade 
    """
    
    
         
    objectsCount = 0
    
    for g in Function['subgraphs']:
        
        if timeout[0] == True:
            print "Breaking out cuz of timeout, time=" + str(int(time.time()-timeout[1])) + " from - func=" + funcfilename + ",exe-" + exeName
            return []
        
        objectsCount += 1
        for refGraphletContainer in GradeSystemsInfoInst:
            
            refGraphlet = refGraphletContainer.getObject()
            
            (isIso,Map12,Map21) = refGraphlet.isomorphic_vf2(g,None,None,None,None,True,False,None,None)
            if isIso:                                      
                
                nodeGradesInfos = []

                for (x,y) in itertools.imap(lambda x,y: (int(x['code']),int(y['code'])),map(lambda x:refGraphlet.vs[x],range(0,len(refGraphlet.vs))),map(lambda x:g.vs[Map12[x]],range(0,len(g.vs)))  ):
                    
                    #nodeGradesInfos.append(gradesCache[x][y])
                    
                    nodeGradesInfos.append(x,y)

                gradeSystemsFinals = OrderedDict()
                
                for methodType in ['contain','ratio']:
                    gradeSystemsFinals[methodType] = numpy.mean(map(lambda nodeGradesInfo: nodeGradesInfo['gradesDict'][methodType],nodeGradesInfos))
            
                
                if "Solver"=="Solver":
                    if gradeSystemsFinals['ratio'] > 50:
                        conDict = GraphletsConstraints(nodeGradesInfos)
                        newTarNodes = list(conDict.getRW())
                        refNodes = map(lambda x:x['refCode'],nodeGradesInfos)
                        grades = map(compareDisAsmCode,refNodes,newTarNodes)
                                            
                        for methodType in ['contain','ratio']:
                            gradeSystemsFinals['Solver_' + methodType] = numpy.mean(map(lambda x:x[methodType],grades))
                            #delta = int(gradeSystemsFinals['Solver_' + methodType] - gradeSystemsFinals[methodType])
                            #refFullCode = ";".join(refNodes)
                            #tarFullCOde = ";".join(newTarNodes)
                            
                        #bestKSolverDeltas.insert({'delta':delta,'ref':refFullCode,'tar':tarFullCOde})
                        #bestKSolverBroken.insert({'broken':conDict.getBrokenNumber(),'ref':refFullCode,'tar':tarFullCOde})
                            
                            #gradeSystemsDict[gradeSystemName]['bestSolImprovmentList'].insert({'delta':delta,'ref':refFullCode,'tar':tarFullCOde}
                    else:
                        for methodType in ['contain','ratio']:
                            gradeSystemsFinals['Solver_' + methodType] = gradeSystemsFinals[methodType]
                else:
                    for methodType in ['contain','ratio']:
                        gradeSystemsFinals['Solver_' + methodType] = numpy.mean(map(lambda nodeGradesInfo: nodeGradesInfo['gradesDict'][methodType],nodeGradesInfos))
                
                for gradeSystemName in gradeSystemNames:
                    refGraphletContainer[gradeSystemName] = max(gradeSystemsFinals[gradeSystemName],refGraphletContainer[gradeSystemName])
                
            
    endForXlsRecord = time.time()
    
    for gradeSystemName in gradeSystemNames: 
        counters = GradeSystemsInfoInst.tallyForGradeSystem(gradeSystemName,borders)
        #counters = gradeSystemsDict[gradeSystemName]['DictCounter'].tallyCounters()
        
        #["exe","funcname","#objects","K","Trace","System","Generator","GradeSystem","TimeStr","TimeNumber"]
        
        fields = [exeName,funcfilename,str(objectsCount),str(myK),"TRUE",methodSystemName,"normal",gradeSystemName,
              "\""+getDurationStr(int(endForXlsRecord-startForXlsRecord))+"\"",str(endForXlsRecord-startForXlsRecord)]
       
            
        for i in range(0,len(borders)):
            fields.append("%.4f" % (float(counters[i]) / float(len(GradeSystemsInfoInst))))

        """            
        if (gradeSystemName == "Solver_contain"):    
            fields.append(str(bestKSolverDeltas.max()))
            fields.append(str(bestKSolverDeltas))
            
            fields.append(str(bestKSolverBroken.max()))
            fields.append(str(bestKSolverBroken))
        else:
            for i in range(0,4):
                fields.append("see Solver_contain")
        
        sets = GradeSystemsInfoInst.detectPatchForGradeSystem(gradeSystemName,[60,70,80])
        sets['total'] = len(tarGraph.vs)
        fields.append(str(sets))
        """
            
        allFields.append(fields)

        
    timeOutTimer.cancel()
    del timeOutTimer
            
    return allFields


def identity(x):
    return x



def CompareWithKSplit():

    refGraph = igraph.read(os.path.join(sourcesDir,sourceFunctionName))
    refGraph['name'] = sourceFunctionName

    if (os.name != "nt"):
        #p = multiprocessing.Pool(initializer=workerInit,initargs=[len(refGraph.vs)])
        p = multiprocessing.Pool()
        mapper = p.imap_unordered
        #mapper = itertools.imap
    else:
        mapper = itertools.imap
        #workerInit(len(refGraph.vs))
    
    reportFile = CounterXlsReport(csvName + "-K=" + str(myK) + "-" + sourceFunctionName) 

    print "Prepping db - (func files) - target=" +os.path.join(sourcesDir,sourceFunctionName)
    sourcesList3k = list(mapper(identity,split2k.ksplitGraphObject(myK,refGraph,True)))
    print "For k=" + str(myK) + " we have - " + str(len(sourcesList3k))
    print "end db prep"
   
    from simple_db import DBSimpleClient

    db = DBSimpleClient()
            
    params =  [doOneFunctionFileRW,itertools.izip(db.get_all(),itertools.cycle([sourcesList3k]))]
    #if (mapper !=  itertools.imap):
    #    params.append(50)       
         
    for allFields in mapper(*params):    
        for fields in allFields:           
            reportFile.writeLine(fields)


if __name__ == '__main__':
    startVal = time.time()
    CompareWithKSplit()
    end = time.time()

    print "total runtime = " + str(getDurationStr(int(end-startVal)))
    
    sendMail()

