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

import os
import sys

import itertools

from myutils import *

import combinatorics
import numpy





# this is a generator for graphlets, in tracemode (only get "sequences", and not "trees")
def ksplitGraphFile(k,fileFullPath,traceMode,returnTupleOnly=False):
    if fileFullPath.find("_intel_") == -1:    # hack to not analyse intel functions...

        g = read(fileFullPath)
        copyGraphAtributesFromRoot(g)
        return ksplitGraphObject(k,g,traceMode)

# this is a generator for graphlets, in tracemode (only get "sequences", and not "trees")
def ksplitGraphObject(k,g,traceMode,returnTupleOnly=False):

    # returns true if graph ok
    def checkGraph(graph,k):
        numOfVertex = len(list(graph.vs))
        assert numOfVertex<=k
        # now check if connected AKA atleast tree
        return  numOfVertex==k and len(list(((graph.as_undirected())).es))>=numOfVertex-1

    for VertexIndex in range(0,len(list(g.vs))):

        lists = list()
        curList = list()
        curDistance = 0

        iter = g.bfsiter(VertexIndex,OUT,True)
        try:
            while curDistance < k:
                (v,dist,father) = iter.next()

                if dist < k:
                    if curDistance < dist:
                        lists.append(curList)
                        curDistance = dist
                        curList = list([int(v['id'])])
                    else:
                        curList.append(int(v['id']))
                else:
                    break
        except StopIteration:
            pass

        lists.append(curList)
        if traceMode:
            seqMaker = itertools.product(*lists)
        else:
            seqMaker = [x[0] for x in combinatorics.m_way_unordered_combinations(list(itertools.chain(*lists)),[k])]

        for seq in seqMaker:
            
            if returnTupleOnly:
                yield seq
            else:
                glist =  list(seq)
                thisg = g.subgraph(glist)
                if checkGraph(thisg,k):
                    name =""
                    for let in glist:
                        if len(name)==0:
                            name += str(let)
                        else:
                            name += "." + str(let)
                    
                    # mor said this gave his some problems and he was right..its not needed anymore.
                    #thisg["FunctionName"] = g['name']  #thisg["name"]
                    thisg["name"] = name
                    thisg["graphletCode"] = ""
                    for node in thisg.vs:
                        thisg["graphletCode"] += node['code'] + ";"
    
                    yield thisg


## load functions ######

"""
#gets dir returns a list with the graphs in the dir loaded to it
def loadGraphsDir(dir):
    l = list()
    for filename in os.listdir(dir):
        otherg = read(os.path.join(dir,filename))
        if (len(otherg.vs) != k):
            raise "Miss match in loaded graphs size, try splitting them on the fly"
        copyGraphAtributesFromRoot(otherg)
        cleanUpGraph(otherg)
        otherg['graphName'] = filename
        l.append(otherg)
        pass
    return l



# this will check this *one* graph and update Identifiers tmp counters
def CreateGraphAdd2List(ngramsList):

    def addGraphToList(candidateGraph,exeName,funcname,graphname):
        ngramsList.append(candidateGraph)

    return addGraphToList
"""




###############################################################################################




"""
def doGetUptoDistanceK(items,g,VertexIndex,k):

    def getUptoDistanceK(g,k,VertexIndex):
        items = set()
        doGetUptoDistanceK(items,g,VertexIndex,k)
        return items

    if k > 0:
        if not items.issuperset(set([VertexIndex])):
            items.add(VertexIndex)
            ls = g.vs[VertexIndex].successors()
            for son in g.vs[VertexIndex].successors():
                doGetUptoDistanceK(items,g,int(son['id']),k-1)
"""

"""
#will call ProcessGraph for every k-graph in functions in inputDir and return total k-graphs processed
def ksplit(k,inputDir,ProcessGraphFunc):

    listing = os.listdir(inputDir)

    count =0

    for infile in listing:
        count +=ksplitFunctionFile(k,inputDir,infile,ProcessGraphFunc)

    return count


def createGraphWriter(baseDir,k):
    outputdir = os.path.join(baseDir,getKdirName(k))
    if os.path.exists(outputdir):
        import shutil
        shutil.rmtree(outputdir)
    os.mkdir(outputdir)

    def GraphWriter(graph2Write,FunctionFileName,graphName):
        copyGraphAtributesToRoot(graph2Write)
        graph2Write.write_gml(os.path.join(outputdir,FunctionFileName.replace(".gml","") + "-" + graphName + ".gml"))

    return GraphWriter

def process():

    if len(sys.argv)>1:
        baseDir = sys.argv[1]
    else:
        baseDir = r"D:\User's documents\technion\project\workset\6.10.gcc\wc_f"
        print "Using default debug path (this will not end well)"

    inputDir = os.path.join(baseDir,"funcgraphs")

    if not os.path.exists(inputDir):
        raise "error, no funcgraphs dir"

    #k=3
    count = ksplit(k,inputDir,createGraphWriter(baseDir,k))
    print "DONE! " +baseDir + " , k=" + str(k) + ", total of [" + str(count) + "] files created"
    #ksplit(4,baseDir,inputDir)
    #ksplit(5,baseDir,inputDir)

if __name__ == '__main__':
    process()
"""