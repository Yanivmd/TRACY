
import re
#from export2xml import *

from IgraphHelper import *

import os

from idaapi import *
from idc import *

from igraph import *

def fillFunctions(functions_dictionary):
    #ea = ScreenEA()

    # this is in case IDA recalcuate it each call...
    fileMD5 = GetInputFileMD5()

    #loop on all segments
    for seg_ea in Segments():

        if (SegName(seg_ea) == ".text"):

            # Loop through all the functions
            for functionEA in Functions(SegStart(seg_ea), SegEnd(seg_ea)):

                function_chunks = []
                func_iter = func_tail_iterator_t(idaapi.get_func(functionEA))

                # While the iterator?s status is valid
                status = func_iter.main()
                while status:
                    # Get the chunk
                   
                    chunk = func_iter.chunk()#

                    # Store its start and ending address as a tuple
                    function_chunks.append({'startEA':chunk.startEA, 'endEA':chunk.endEA})

                    # Get the last status
                    status = func_iter.next()
                
                #print "got chunk!, funcname =" +  GetFunctionName(functionEA)
                #if function_chunks != [{'startEA':GetFunctionAttr(functionEA,FUNCATTR_START), 'end_ea':GetFunctionAttr(functionEA,FUNCATTR_END)}]:
                #    print "Chunks =" + str(function_chunks)
                #    print "Func=" + str({'startEA':GetFunctionAttr(functionEA,FUNCATTR_START), 'end_ea':GetFunctionAttr(functionEA,FUNCATTR_END)})
                #    raise hell
                
                function_chunks.sort(key=lambda x: x['startEA'])
                functions_dictionary.append(Graph(0,[],True,{'startEA':GetFunctionAttr(functionEA,FUNCATTR_START), 'endEA':GetFunctionAttr(functionEA,FUNCATTR_END),'name': GetFunctionName(functionEA),
                                                        'fileMd5':fileMD5,'filePath':GetInputFilePath(),'chunks':function_chunks}))




################  pipeline stages functions...(take function graph, perform action on reference)   ##########



def pred_print(func_dict):
    addr = func_dict['startEA']
    print "function = " + hex(addr) + "start=" +str(func_dict['startEA'])
    while (addr<func_dict['endEA']):
        print GetDisasm(addr)
        addr=NextHead(addr,addr+100)

    #print func_dict['edges']


# this pred turnes function to disasm text, where presentCode is with comments and originalCode is pure code.
def pred_2str(func_dict):
    addr = func_dict['startEA']
    presentedCode = ""
    originalCode = ""
    # subroutine marked as ended one line after the real end.
    while (addr<func_dict['endEA']):
        presentedCode += GetDisasm(addr) + ';'
        originalCode += getOriginalCodeFromAddr(addr)
        addr=NextHead(addr,addr+100)

    func_dict['presentCode'] = presentedCode.replace('"',"'")
    func_dict['originalCode'] = originalCode.replace('"',"'")


def remove_str(func_dict):
    func_dict['presentCode'] = ""
    func_dict['originalCode'] = ""



def CreateFuncGraphs(func_dict):
    
    #edges = set()
    #boundaries = set((f_start,))

    #print func_dict['name'] + " start=" + hex(func_dict['startEA']) + " end=" + hex(func_dict['endEA'])

    func_g = FunctionGraph(func_dict)
    
    #print "Func=" + func_dict['name'] 
    #print "Start=" + str(func_dict['startEA'])
    #print "End =" + str(func_dict['endEA'])
    #print "chunks = " + str(func_dict['chunks'])
    
    for chunk in func_dict['chunks']:
        f_start =chunk['startEA']
        #f_end = FindFuncEnd(func_dict['startEA'])
        f_end = chunk['endEA']
    
        for head in Heads(f_start, f_end):
    
            if isCode(GetFlags(head)):
    
                #idaapi.XREF_FAR (AKA 1) -> this will treat each line as call...so use 0
                to_refs = CodeRefsTo(head, 0)
                to_refs = list(filter(lambda x: x>=f_start and x<f_end, to_refs))
    
                if ((len(to_refs) >= 1)):
                    # we need to break at the LAST head!
                    func_g.cutCorrent()
                    created = func_g.addLine2Current(head)
                    for ref in to_refs:
                        func_g.connectCorrent2addr(ref,False)
                else:
                    created = func_g.addLine2Current(head)
    
                if (created):
                    # TODO- y list list?
                    if (len(list(list(filter(lambda x: x==func_g.getLastVertexEndEA() , CodeRefsTo(head, 1))))) >0 ):
                        #print "connecting last to this!"
                        func_g.connectLastToCurrent()
    
                from_refs = CodeRefsFrom(head, 0)
                from_refs = list(filter(lambda x: x>=f_start and x<f_end, from_refs))
    
    
                if ((len(from_refs) >= 1)):
                    for ref in from_refs:
                        func_g.connectCorrent2addr(ref,True)
                    func_g.cutCorrent()
    
                #print "head = " + hex(head) + " , tolen=" + str(len(list(filter(lambda x: x>=f_start and x<=f_end, CodeRefsTo(head, 1))))) + " fromlen=" + str(len(list(filter(lambda x: x>=f_start and x<=f_end, CodeRefsFrom(head, 1)))))
                #print "head = " + hex(head) + " , tolen=" + str(len(to_refs)) + " fromlen=" + str(len(from_refs))
    
    
                """if refs:
                    next_head = NextHead(head, f_end)
                    if isFlow(GetFlags(next_head)):
                        refs.add(next_head)
    
                    boundaries.union_update(refs)
    
                    for r in refs:
    
                        if isFlow(GetFlags(r)):
                            edges.add((hex(PrevHead(r, f_start)), hex(r)))
                        edges.add((hex(head), hex(r)))"""
    

    #if func_g.debt_count != 0:
    #    func_g.func_graph.write_gml("d:\\t.gml")

    func_g.Checkdebt()

    func_dict['vertexCount'] = func_g.vertexCount



def checkIdioms(func_dict):
    for idiom  in idioms:
        # TODO change this...its really stupid
        idiom['number'] = idioms.index(idiom)+1
        match = re.search(idiom['str'],func_dict['string'],flags=0)
        if match != None:
            func_dict['Matchs'].append(idiom['effect'](idiom))

"""

def go_over_func(func_dict,predicates):


    #if (str(func_dict['Matchs']) != '[]' and 1==0):
    #    print "function " + func_dict['name'] + ", from " + hex(func_dict['startEA']) + " to " + hex(func_dict['endEA'])
    #    print "found this - " + str(func_dict['Matchs'])
"""

##############################################################################################################################

def doitall():
    idaapi.autoWait()
    outputdir = functionsGraphsDirectoryName #$+ "-" + GetInputFile()

    if os.path.exists(outputdir):
        #import shutil
        #shutil.rmtree(outputdir)
        #os.mkdir(outputdir)
        pass
    else:
        os.mkdir(outputdir)


    functionPipeLine = [pred_2str,CreateFuncGraphs]
    #predicates_with_print = [pred_2str,CreateFuncGraphs,pred_print]

    functions = []
    fillFunctions(functions)

    #print len(functions)

    for func in functions:
        """#if (func['name'].lower() =="_main" or func['name'].lower()=="main"):
        if (func['name'].lower()=="__libc_csu_init"):
            go_over_func(func,functionPipeLine)
        else:
            pass
            go_over_func(func,functionPipeLine)"""

        for stage in functionPipeLine:
            stage(func)


    MaxVer = 1
    g = None
    Name = ""
    counter = 0;

    excludeList = list()
    excludeList.append("twinID")

    for func in functions:
        filenameGml =  func['name'].replace('?','') + ".gml"
        filenameDsm =  func['name'].replace('?','') + ".dsm"
        
        
        f = open(os.path.join(outputdir,filenameDsm),"w")
        f.write(func['originalCode'])
        f.close()
        

        if func['vertexCount'] > MaxVer:
            MaxVer = func['vertexCount']
            g = func
            Name = func['name']


        copyGraphAtributesToRoot(func)

        # the old code does DFS, i want BFS so ill copy the graph..:\
        # this will also lose the filler nodes (lea esi,[lea+0] without a parent)
        # in the first pass we just copy and mark ids

        # this is always true because the way the graph was built...
        rootNode = func.vs[0]
        iter = func.bfsiter(rootNode,OUT,True)

        # new directed graph
        newFuncGraph = Graph(0,[],True)
        copyIgraphObjectAttributes(func,newFuncGraph,None)
        
        for (node,dist,parent) in iter:
            newFuncGraph.add_vertex()
            currentVertexId = len(newFuncGraph.vs)-1
            currentVertex = newFuncGraph.vs[currentVertexId]

            copyIgraphObjectAttributes(node,currentVertex,excludeList)
            currentVertex['id'] = currentVertexId
            node['twinID'] = currentVertexId

            if (parent != None):
                newFuncGraph.add_edge(parent['twinID'],currentVertexId)

            MakeComm(currentVertex['startEA'],"NODEID=" + str(currentVertexId))

        #in the second pass we will set the nodes entry and exit nodes
        
        newRootNode = newFuncGraph.vs[0]
        newIter = newFuncGraph.bfsiter(newRootNode,OUT,False)
        
        for node in newIter:
            node['outNodes'] = "<" + ",".join(map(lambda x:str(x['id']), node.neighbors(OUT))) + ">"
            node['inNodes'] = "<" + ",".join(map(lambda x:str(x['id']), node.neighbors(IN))) + ">"


        graphFullPath = os.path.join(outputdir,filenameGml)

        if (not (os.path.exists(graphFullPath))):
            newFuncGraph.write_gml(graphFullPath)
            #print counter
            counter+=1

            if counter==500:
                break
        else:
            print "Not re-writing - " + func['name'] + " (in - " + graphFullPath + ")"

    if counter<500:
        print "max - " + str(MaxVer) + " name=" + Name
    else:
        print "partial result, run again (igraph bug, cannot load too many files.."
        raise hell
        Exit(1)


#==========================================================================#
from idaapi import *
from idc import *

class FunctionGraph:
    Name = "FunctionGraph"

    def __init__(self,graph):
        self.func_graph = graph
        self.vertexCount = 0
        self.currentVertex = None
        self.lastVertex = None
        self.firstEver = True
        self.debt_count = 0;


    """def getCodeLine(self,addr):

        return getOriginalCodeFromAddr(addr)

    
        if GetOpType(addr,0) == o_near and self.func_graph['startEA'] <= GetOperandValue(addr,0) and GetOperandValue(addr,0) < self.func_graph['endEA']:

            #this is a jump, if its inside the func we want to save offset as relative to current addr
            return GetMnem(addr) + " roffset_" + hex(  (addr-(GetOperandValue(addr,0)) + (1 << 32)) % (1 << 32)) + ";"

        else:
            return getOriginalCodeFromAddr(addr)
    """


    # return true if new node is created
    def addLine2Current(self,addr):

        if (self.currentVertex == None):
            self.func_graph.add_vertex()
            self.vertexCount+=1
            self.currentVertex =self.func_graph.vs[self.vertexCount-1]
            self.currentVertex['code'] = ""
            self.currentVertex['startEA'] = int(addr)
            #self.currentVertex['HstartEA'] = hex(addr)
            #this is for sanity - count all the forward edges that i dont set...
            self.firstEver = False
            #print "NEW EDGE!!!"
            created = True
        else:
            created = False

        if GetOpType(addr,0) == o_near and self.func_graph['startEA'] <= GetOperandValue(addr,0) and GetOperandValue(addr,0) < self.func_graph['endEA']:
            self.currentVertex['jumpCodeRelative'] = GetMnem(addr) + " roffset_" + hex(  (addr-(GetOperandValue(addr,0)) + (1 << 32)) % (1 << 32)) + ";"
            self.currentVertex['jumpCodeOriginal'] = getOriginalCodeFromAddr(addr)
        else:
            self.currentVertex['code'] += getOriginalCodeFromAddr(addr)
            
        self.currentVertex['endEA'] = int(addr)

        return created

    #will return none if donesnt exist..
    def getVertexForAddr(self,addr):
        #print " i am - " + str(self.currentVertex['startEA']) + " looking for -" + str(addr)
        ls = list(self.func_graph.vs.select(lambda x: x['startEA']<=int(addr) and x['endEA']>=int(addr)))
        #make sure we dont have a conflict
        assert (len(ls)<=1)

        if (len(ls)>0):
            #print "found!"
            return ls[0]
        else:
            #print "not found"
            return None


    #if fromCurrent is true, we connect current to addr, otherwise the other way around
    def connectCorrent2addr(self,addr,fromCurrent):
        assert (self.firstEver==False and self.currentVertex != None)
        otherEnd = self.getVertexForAddr(int(addr))
        if (otherEnd != None):
            #print "NEW EDGE!!!"
            self.debt_count-=1
            if (fromCurrent):
                self.func_graph.add_edge(self.currentVertex,otherEnd)
            else:
                self.func_graph.add_edge(otherEnd,self.currentVertex)
        else:
            self.debt_count+=1

    def cutCorrent(self):
        #print "CUT!"
        if (self.currentVertex != None):
            self.lastVertex = self.currentVertex
            self.currentVertex = None

    def Checkdebt(self):
        #print " debt==[" + str(self.debt_count) + "]"
        #assert (self.debt_count==0)
        pass


    def printNodes(self):
        for item in self.func_graph.vs:
            print "start=[" +str(item['startEA']) + "] end=[" +str(item['endEA']) + "]"

    def printEdges(self):
        for item in self.func_graph.es:
            print item.attributes()
            #print "start=[" +str(item['startEA']) + "] end=[" +str(item['endEA']) + "]"

    def getLastVertexEndEA(self):
        if (self.lastVertex != None):
            return self.lastVertex['endEA']
        else:
            return -1

    def connectLastToCurrent(self):
        self.func_graph.add_edge(self.lastVertex,self.currentVertex)



#ida adds comments that we dont want for the compare...
def getOriginalCodeFromAddr(ea):
    line = GetMnem(ea)
    #print ea
    op1 = GetOpnd(ea,0)
    op2 = GetOpnd(ea,1)

    if op1 != "":
        line += " " + op1
        if op2 != "":
            line += "," + op2
    line += ";"
    return line


#===========================================================================

if __name__ == '__main__':
    doitall()
    Exit(1)

