#-------------------------------------------------------------------------------
# Name:        myutils
# Purpose:
#
# Author:      user
#
# Created:     12/08/2012
# Copyright:   (c) user 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python


#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

import os
import itertools


#import GraphletsCompareDiff
#import GraphletsCompareMy
#import ngrams
#import colorGraphs

functionsGraphsDirectoryName = "funcgraphs"

graphAttribPrefix = "GRAPH"


"""

#right not we load these config dicts with the graphlets...its the only reason these are not params...
def getDiffConfigs():
    return [{'K':1,'Trace':True},{'K':2,'Trace':True},{'K':3,'Trace':True},{'K':3,'Trace':False}]

def normalCodeDiff(x):
    return x['code']

def getDiffParams():
    return  {
             'compareSystems':[
                               {'compareFuncsGenerator':GraphletsCompareMy.getCompareMethods,'name':'My'},
                               {'compareFuncsGenerator':GraphletsCompareDiff.getCompareMethods,'name':'DIFF'}
                               ],
             'codeGenerators':[
                            {'function':normalCodeDiff,'name':'ignore'},
                            #{'generator':lambda x:x['code']+x.get('jumpCodeOriginal',""),'name':'original'},
                            #{'generator':lambda x:x['code']+x.get('jumpCodeRelative',""),'name':'relative'},
                            ]
             }


def getNgramsConfigs():
    return [{'windowSize':5,'delta':1,'Trace':True}]

def normalCodeNgram(x):
    return x['code']

def getNgramsParams():
    return  {
             'compareSystems':[
                               {'compareFuncsGenerator':ngrams.getCompareMethods,'name':'5-gram'},
                               ],
             'codeGenerators':[
                            {'function':normalCodeNgram,'name':'ignore'},
                            #{'generator':lambda x:x['code']+x.get('jumpCodeOriginal',""),'name':'original'},
                            #{'generator':lambda x:x['code']+x.get('jumpCodeRelative',""),'name':'relative'},
                            ]
             }

def getColorConfigs():
    return [{'K':5,'Trace':False}]

def normalCodeColor(x):
    return x

def getColorParams():
    return  {
             'compareSystems':[
                               {'compareFuncsGenerator':colorGraphs.getCompareMethods,'name':'colorCompare'},
                               ],
             'codeGenerators':[
                            {'function':normalCodeColor,'name':'Graph'},
                            #{'generator':lambda x:x['code']+x.get('jumpCodeOriginal',""),'name':'original'},
                            #{'generator':lambda x:x['code']+x.get('jumpCodeRelative',""),'name':'relative'},
                            ]
             }

"""
borders = range(10,110,10) # [10, 20, 30, 40, 50, 60, 70, 80, 90,100]  
#[60,70,85,90,95,100]
traceBorder = 70
rewriteBorder = 70

def getKdirName(k):
    return "k" + str(k)+ "graphs"

def getNgramsDirName(window,delta):
    return "ngrams-" +str(window) +"X"+ str(delta)

# this will copy the graph attributes to the first vertex to bypass the bug with loading graph attributes
def copyGraphAtributesToRoot(g):
    #RLS!!    #print g.attributes()
    cleanUpGraph(g)
    #for v in g.vs:    #    cleanUpObject(v)    #END OF RLS


def copyIgraphObjectAttributes(srcObj,dstObj,excludeList):
    for attrib in srcObj.attributes():
        if excludeList != None and excludeList.count(attrib) == 0:
            dstObj[attrib] = srcObj[attrib]

def copyGraphAtributesFromRoot(g):
    for attrib in g.vs[0].attributes():
        #pass
        #print str(attrib) + str(g[attrib])
        if (attrib.find(graphAttribPrefix)==0):
            g[attrib.replace(graphAttribPrefix,'')] = g.vs[0][attrib]
            g.vs[0][attrib] = None
            del g.vs[0][attrib]

        #del g[attrib]



# this will remove all the things we dont need from the graph..(so they could be garbge collected)
def cleanUpGraph(obj):
    obj['presentCode']=""
    del obj['presentCode']
    obj['originalCode'] = ""
    del obj['originalCode']




#this will return 0 if both dont accomidate predicate, 1 if both accomidate, and -1 if 1 doesnt and 2 does, or -2 the other way around.
def iff(pred,obj1,obj2):
    if pred(obj1):
        if pred(obj2):
            return 1
        else:
            return -2
    else:
        if pred(obj2):
            return -1
        else:
            return 0

def getMatchingNodes(refGraphlet,tarGraphlet,nodeCodeGenerator):
    (isIso,Map12,Map21) = refGraphlet.isomorphic_vf2(tarGraphlet,None,None,None,None,True,False,None,None)
    if isIso:
        #if Map12 != [0,1,2]:
        #    raise hell

        refNodes = []
        tarNodes = []
        for i in range(0,len(tarGraphlet.vs)):
            refNodes.append(nodeCodeGenerator(refGraphlet.vs[i]))
            tarNodes.append(nodeCodeGenerator(tarGraphlet.vs[Map12[i]]))

        return (refNodes,tarNodes)
    else:
        return (None,None)


def getDurationStr(t):
    days = t / (60 * 60 *24)
    t = t % (60 * 60 *24)
    hours = t / (60 * 60)
    t = t % (60 * 60)
    mins = t / 60
    t = mins % 60
    secs = t
    return "d=" + str(days) + ",h=" + str(hours) + ",m=" + str(mins) +",s=" + str(secs)


##################### deal with xls's        ###############

class XlsReport:

    def __init__(self,fileName,fields,appendOnExists=False):
        self.resFileName = fileName
        fullPath = os.path.join("..","Results",self.resFileName)
        self.fields = fields

        #if not os.path.exists(fullPath):
        self.reportFile = open(fullPath,"w")
        self.reportFile.write(",".join(fields) + "\n")
        #else:
        #    self.reportFile = open(fullPath,"a")
    
    
    def __exit__(self):
        print "closing XlsReport log file!"
        self.reportFile.close()

    def flush(self):
        self.reportFile.flush()

    def writeLine(self,fieldsToWrite):
        if len(self.fields) != len(fieldsToWrite):
            print "Field Problem - needed=" + str( len(self.fields)) + " got=" + str(len(fieldsToWrite))
            print "got-[" + str(fieldsToWrite) + "]"
            raise hell

        for i in range(0,len(fieldsToWrite)):
            if " " in fieldsToWrite[i]:
                fieldsToWrite[i] = "\"" + fieldsToWrite[i].replace("\"","'") + "\""

        #if (tracePrints):
        #    print fieldsToWrite

        self.reportFile.write(",".join(fieldsToWrite) +"\n")


class CounterXlsReport(XlsReport):

    def __init__(self,reportName):
        fields = ["exe","funcname","#objects","K","Trace","System","Generator","GradeSystem","TimeStr","TimeNumber"]
        for border in borders:
            fields.append("match-" + str(border))
        
        #fields.append("Delta-MAX")
        #fields.append("Delta-INFO")
        #fields.append("Broken-MAX")
        #fields.append("Broken-INFO")
        #fields.append("Patch-INFO")
        XlsReport.__init__(self,"resreport[" + reportName + "].csv",fields)
        pass

    def writeResults(self,exeName,current_function,K,Trace,System,TimeStr,TimeNumber,dictCounterInst):

        counters = dictCounterInst.tallyCounters()
        fields = [exeName,current_function,K,Trace,System,TimeStr,TimeNumber]
        for i in range(0,len(borders)):
            fields.append("%.4f" % (float(counters[i]) / float(dictCounterInst.getMax())))

        self.writeLine(fields)

        #if (tracePrints):
        #    print fields

        self.reportFile.flush()

    def __exit__(self):
        print "closing CounterXlsReport log file!"
        super(CounterXlsReport,self).__exit__()


class TraceXlsReport(XlsReport):

    def __init__(self,reportName):
        fields = ["exe","funcname","nodeGrades","nodeGradesMean","RWDict","refName","tarName","refCode","tarCode"]
        XlsReport.__init__(self,"resreportTRACE[" + reportName + "].csv",fields)
        pass

    def __exit__(self):
        print "closing CounterXlsReport log file!"
        super(CounterXlsReport,self).__exit__()
        
        
#######################################################################################################################

#### this will help turn any dict of igraph.graph into a counter




class GradeSystemsInfo:
    
    class ContainerObject:
        def __init__(self,inObject,gradeSystemNames):
            self.counter = 0
            self.inObject = inObject
            self.gradeSystemNames = gradeSystemNames
            self.gradeSystems = {}
            for gradeSystemName in self.gradeSystemNames:
                self.gradeSystems[gradeSystemName] = 0
        
        def __getitem__(self, key): 
            return self.gradeSystems[key]
        
        def __setitem__(self, key,value): 
            self.gradeSystems[key] = value
            
        def getObject(self):
            return self.inObject

    
    def __init__(self,internalCollection,gradeSystemNames):
        self._items = map(lambda item: GradeSystemsInfo.ContainerObject(item,gradeSystemNames),internalCollection)
    
    def __iter__(self):
        for item in self._items:
            yield item
            
    def tallyForGradeSystem(self,gradeSystemName,borders):
        
        counters = list(map(lambda x:0,borders))
        for item in self._items:
            # this is for above grade 0
            maxGrade = item[gradeSystemName]
            for (index,border) in enumerate(borders):
                if maxGrade >= border:
                    counters[index] += 1
                    
        return counters
    
    
    def detectPatchForGradeSystem(self,gradeSystemName,borders):
        
        counters = {}
        for border in borders:
            counters[border] = set()
        for item in self._items:
            # this is for above grade 0
            maxGrade = item[gradeSystemName]
            for border in borders:
                if maxGrade > border:
                    for nodeNumber in map(int,item.getObject()['name'].split(".")):
                        counters[border].add(nodeNumber)
                
        return counters
    
            
    def items(self):
        return self._items
    
    def __len__(self):
        return len(self._items)    


"""
class dictCounter:

    def __init__(self,group,identifierName):
        self.group = group
        self.identifierName = identifierName

    #these function will turn any dict object to a counter of a property, for each border
    def resetCounters(self):
        #for identifier in Identifiers:
        Group = self.group
        for member in Group:
            for border in borders:
                member['tmpCounter-' + str(border)] =0


    def printCounters(self):
        Group = self.group
        identifierName = self.identifierName
        #for identifier in Identifiers:
        for member in Group:
            resStr = "Name=" + str(member[identifierName])
            for border in borders:
                resStr+= " match-" + str(border) + "=" + str(member['tmpCounter-' + str(border)])
            print resStr

    def updateCounters(self,newGrade,member):
        for border in borders:
            if newGrade >= border:
                member['tmpCounter-' + str(border)] +=1

    def cleanupCounters(self):
        Group = self.gorup
        #for identifier in Identifiers:
        for member in Group:
            for border in borders:
                del member['tmpCounter-' + str(border)]

    def tallyCounters(self):
        Group = self.group
        int_counter =  [0] * len(borders)
        for member in Group:
            for i in range(0,len(borders)):
                if member['tmpCounter-' + str(borders[i])]>0:
                    int_counter[i]+=1

        return int_counter

    def getMax(self):
        return len(self.group)
"""
"""


idioms = [
    {'str':'push\s+ebp;[^;]+;mov\s+ebp\s+,\s+esp;','effect': lambda idiom: "match"+str(idiom['number'])},
    {'str':'^push\s+ebp;.*mov\s+esp\s*,\s*ebp;','effect': lambda idiom: "match"+str(idiom['number'])},
    {'str':'test\s+ebp\s*,\s*esp;','effect': lambda idiom: "match"+str(idiom['number'])},
    {'str':'adc\s+esi\s*,\s*esi;','effect': lambda idiom: "match"+str(idiom['number'])}
    ]


def compareWithk3Files():

    print "Prepping db -(3k files)"
    Identifiers = [
        {'name':sourceFunctionName,'graphs':loadGraphsDir(sourceDir)}
    ]
    print "end db prep"

    resFileName = "resreport[" + sourceFunctionName + "].csv"

    if not os.path.exists(resFileName):
        reportFile = open(resFileName,"w")
        reportFile.write("exe,funcname,match\n")
    else:
        reportFile = open(resFileName,"a")


    memlimit = 30000
    #memlimit = 2512


    for exeName in os.listdir(candidatesDir):
        print "Loading - " + exeName + " ... " ,

        resetIdentifiers(Identifiers)

        current_function= "" #empty string doesnt match to function, function name must be != E

        candidateGraphs = list()
        candidateDir = os.path.join(candidatesDir,os.path.join(exeName,"k3graphs"))
        #p = 0
        for filename in os.listdir(candidateDir):
            try:

                # did we finish a function?
                if (filename.split("-")[0] != current_function) :
                    if (current_function != ""):
                        checkLastFunction(candidateGraphs,Identifiers,reportFile,exeName,current_function)

                        del candidateGraphs
                        candidateGraphs = list()

                        resetIdentifiers(Identifiers)

                    current_function = filename.split("-")[0]

                otherg = read(os.path.join(candidateDir,filename))
                copyGraphAtributesFromRoot(otherg)
                cleanUpGraph(otherg)
                otherg['graphName'] = filename
                candidateGraphs.append(otherg)

                if (sys.getsizeof(candidateGraphs)+ sys.getsizeof(Identifiers)) > memlimit  :
                    #print " Partly loaded, out of memory! checking - " + str(len(candidateGraphs)) + " graphs , " ,
                    checkGraphs(candidateGraphs,Identifiers)
                    #this is maybe not needed...
                    del candidateGraphs
                    candidateGraphs = list()
                    cleared =gc.collect()
                    if len(gc.garbage) > 0:
                        print "Error! - gar>0 =[" + str(gc.garbage) + "]"
                    print ".",
                    pass

                pass
            except MemoryError:
                #print " !!MemoryError!! Partly loaded, checking - " + str(len(candidateGraphs)) + " graphs , " ,
                cleared =gc.collect()

                checkGraphs(candidateGraphs,Identifiers)
                #this is maybe not needed...
                del candidateGraphs
                candidateGraphs = list()
                cleared =gc.collect()
                print ".",
                if len(gc.garbage) > 0:
                    print "Error! - gar>0 =[" + str(gc.garbage) + "]"



        print ".",

        checkLastFunction(candidateGraphs,Identifiers,reportFile,exeName,current_function)

        del candidateGraphs
        cleared =gc.collect()
        if len(gc.garbage) > 0:
            print "Error! - gar>0 =[" + str(gc.garbage) + "]"


    print " DONE!"

    reportFile.close()
"""