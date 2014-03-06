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

def main():
    #g = Graph.Read_GraphMLz(r"D:\User's documents\technion\project\workset\6.12.gcc\funcgraphs\.realloc.gml")
    #
    
    if 1==0:
        g = Graph()
        
        g.add_vertex()
        g.add_vertex()
        g.add_vertex()
        g.add_vertex()
        
        g.add_edge(0,1)
        g.add_edge(0,2)
        g.add_edge(2,3)
    else:
        g = read(r"D:\getftp.gml")
        g.vs[0]['color'] = 'green'
   # g.vs["label"] = g.vs["HstartEA"]


    #print g["asd"]
    #print g['name']
   #g.is

    #plot(g)


    #g = Graph()
    #g.add_vertex(2)
    #g.add_edge(0,1)

    #g['check'] = 'asd'

    #  is cool
        
    # bad = "rt_circular","rt"
    # good = "grid"     
    
    styleList3d = ["drl_3d","grid_3d","kk_3d","fr_3d"]
    #"auto","circle","drl"
    #styleList =["fr","grid","graphopt","gfr","kk","lgl","mds","sphere","star","sugiyama"]

    """
    for plotStyle in ["grid"]:
        print plotStyle
        plot(g,layout=plotStyle ,bbox = (1600, 1600), margin = 20)
        
    print "DONE"
    """
    plot(g,layout="rt" ,root=0,bbox = (1600, 1600), margin = 20)
    #plot(g1)

if __name__ == '__main__':
    main()
