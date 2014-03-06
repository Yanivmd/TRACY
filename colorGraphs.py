
from split2k import *

from igraph import *

import myutils

from difflib import *

import math


colorDict = [
                { 'prefixs':["movs","cmps","sca","lod","stos","rep"]     ,'name':"String"},
                { 'prefixs':["mov","cmov","cwd","cdq"]        ,'name':"DataTransfer"},
                { 'prefixs':["push","pop"] ,'name':"Stack"},
                { 'prefixs':["sub","add","shr","shl","sbb","sar","adc","xchg","imul","idiv","mul","div","inc","dec","xadd","ror","rol"]  ,'name':"Arithmetic"},
                { 'prefixs':["call"]       ,'name':"Call"},
                { 'prefixs':["lea"]        ,'name':"LEA"},
                { 'prefixs':["in","out"]        ,'name':"IO"},
                { 'prefixs':["cmp","test","comiss","ucomi"]        ,'name':"Test"},
                { 'prefixs':["jmp"]        ,'name':"Jump"},
                { 'prefixs':["nop","hlt","mfence","sldt"]        ,'name':"SKIP"},   # this is mosly stuff IDA puts in..i want to skip it for now.
                { 'prefixs':["ret"]        ,'name':"SKIP"},   # this was not mentioned in the artical, so i'll skip it
                { 'prefixs':["and","xor","not","or","bt","bsr","neg"]        ,'name':"Logic"},
                { 'prefixs':["set","sahf","cld"]        ,'name':"Flags"},
                { 'prefixs':["fld","cvt","vcvt","maxss","pun","shufps","sqrt","unpck","f"]        ,'name':"Float"}, # we can do this cuz order matters...
                { 'prefixs':["j"]        ,'name':"Jump"},  # we can do this cuz order matters...
                { 'prefixs':["p"]        ,'name':"Arithmetic"} # this is for all 64bit arithmetic commands, we can do this cuz order matters...
]



def getCompareMethods():
    yield MatchingColorGraphs
    

def CompareNodeColor(g1,g2,v1,v2):
    set1 = g1.vs[v1]['colorSet']
    set2 = g2.vs[v2]['colorSet']
    return set1.issubset(set2) and set2.issubset(set1)

def MatchingColorGraphs(g1,g2):
    (refNodes,tarNodes) = myutils.getMatchingNodes(g1,g2,lambda x:x)
    if (refNodes == None):
        return {'normal':0,'color':0}

    for (v1,v2) in zip(refNodes,tarNodes):
        set1 = v1['colorSet']
        set2 = v2['colorSet']
        if not (set1.issubset(set2) and set2.issubset(set1)):
            return {'normal':100,'color':0}
    
    return {'normal':100,'color':100}
        

def ksplitColorGraphObject(k,graph):
    addNodeColors(graph)
    for graphlet in ksplitGraphObject(k,graph,False):
        yield graphlet

def addNodeColors(candidateGraph):
        g =candidateGraph
        for v in g.vs:
            colorSet = set()
            code = v['code']
            
            if 'jumpCodeOriginal' in v.attributes():
                # there is bug that causes this value to be NaN (which is float for infinity) so handle this 
                if type(v['jumpCodeOriginal']) is str and type(v['jumpCodeOriginal']) != None and v['jumpCodeOriginal'] != "" and v['jumpCodeOriginal'] != "None":
                    code += v['jumpCodeOriginal']
               
            for cmd in code.split(';'):
                if (len(cmd)>0):
                    
                    if cmd == "None":
                        print "NONE FOUND IN CODE=" + str(code)+ " g['name']" + g['name']
                        for attrib in g.attributes():
                            print str(attrib) + "->" + str(g[attrib])
                            
                        exit()
                    
                    foundColor = ""

                    for colorRecord in colorDict:
                        for option in colorRecord['prefixs']:
                            if (cmd.startswith(option)):
                                foundColor = colorRecord['name']
                                break

                        if (foundColor != ""):
                            break

                    if (foundColor == ""):
                        #print cmd
                        #raise Exception("Unknown cmd" + cmd)
                        print "Unknown cmd " + str(cmd) #+ ",in code=" + str(code)
                    else:
                        if (foundColor != "SKIP"):
                            colorSet.add(foundColor)

            v['colorSet'] = colorSet;

"""
# this will check this *one* graph and update Identifiers tmp counters
def CreateGraphAdd2List(myList):

    def addGraphToList(candidateGraph,funcname,graphname):
        myList.append(candidateGraph)

    return addGraphToList


#gets dir returns a list with the graphs in the dir loaded to it
def loadColorGraphsFuncFile(funcDir,funcFileName):
    l = list()

    colorKSplitFunctionFile(k,funcDir,funcFileName,CreateGraphAdd2List(l))

    return l


def createColorFilter(upperProcessFunc):
    def addColor(candidateGraph,funcname,graphname):
        upperProcessFunc(candidateGraph,funcname,graphname)
        return
        g =candidateGraph
        for v in g.vs:
            colorSet = set()
            for cmd in v['code'].split(';'):
                if (len(cmd)>0):
                    foundColor = ""

                    for colorRecord in colorDict:
                        for option in colorRecord['prefixs']:
                            if (cmd.startswith(option)):
                                foundColor = colorRecord['name']
                                break

                        if (foundColor != ""):
                            break

                    if (foundColor == ""):
                        #print cmd
                        #raise Exception("Unknown cmd" + cmd)
                        print "Unknown cmd " + cmd
                    else:
                        if (foundColor != "SKIP"):
                            colorSet.add(foundColor)

            v['colorSet'] = colorSet;

        upperProcessFunc(candidateGraph,funcname,graphname)

    return addColor





# this will check this *one* graph and update Identifiers tmp counters
def CreateCheckOneColorGraph(Identifiers):

    def checkOneColorGraph(candidateGraph,funcname,graphname):
        for identifier in Identifiers:
            for identifierGraph in [x for x in identifier['graphs'] if x['tmpCounter'] == 0]:

                if MatchingColorGraphs(candidateGraph,identifierGraph):
                    identifierGraph['tmpCounter']+=1
                    #break

    return checkOneColorGraph
"""