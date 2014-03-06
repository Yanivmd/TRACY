functionsGraphsDirectoryName = "funcgraphs"
graphAttribPrefix = "GRAPH"

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
