import itertools

from constraint import Problem,MinConflictsSolver

from x86Analyzer import X86AnalyzerBase


traceHack = False

class GraphletsConstraints(X86AnalyzerBase):
    
    #__registers32Bit = ["eax","ebx","ecx","edx","esi","edi","ebp","esp"]
    
    __dictNames = ['ref','tar']
    
    __printConds = False
    
    def __init__(self,nodeGradesInfos=[]):

        X86AnalyzerBase.__init__(self,nodeGradesInfos)
        self.problem = Problem(MinConflictsSolver())
        # this is to make it human readable ..
        # we will generator the solution only when we need it and then cache it
        
        # TODO make __
        self.sol = None 
        
        for key in self.rewriteDict.keys():
            self.rewriteDict[key]['symbolCache'] = {}
            self.rewriteDict[key]['curLine'] = 1
            self.rewriteDict[key]['curPos'] = 1
        
        self.createRewrite()
    
    def getEmptyDict(self):
        d = X86AnalyzerBase.getEmptyDict(self)
        for key in d.keys():
            d[key]['transitions'] = []
            d[key]['valuesTrackDict'] = {}
            #if key != self.REGISTER:
            d[key]['domain'] = set()
            #self.rewriteDict[key]['inCmdCounter'] = 1
            
        return d
    
    # this will add recorded value to dict, even if there is a conflict it will be recorded...
    #
    def insertToDictWithType(self,tarCmdNum,fromStr,refCmdNum,toStr,typeStr,dict2insert=None):

        assert(dict2insert != None)
        dict2insert[typeStr]['transitions'].append((tarCmdNum,fromStr,toStr))
        
        #if typeStr != self.REGISTER:
        dict2insert[typeStr]['domain'].add(toStr)
            

    def commitChanges(self,tmpDict):
        for key in self.rewriteDict.keys():
            self.rewriteDict[key]['transitions'].extend(tmpDict[key]['transitions'])
            #if key != self.REGISTER:
            self.rewriteDict[key]['domain'].update(tmpDict[key]['domain'])
        

    # black list has no generation:) , we can use the rwdict type as they are the same..
    def getRewriteWithType(self,tarCmdNum,fromStr,typeStr,FoundBlacklistElement):
        
        if self.sol == None:
            self.callSol()

        if self.rewriteDict[typeStr]['curLine'] < tarCmdNum :
            self.rewriteDict[typeStr]['curLine'] = tarCmdNum
            self.rewriteDict[typeStr]['curPos'] = 1

            
        varName = self.getVarName(self.getShort(typeStr), tarCmdNum, self.rewriteDict[typeStr]['curPos'])
        self.rewriteDict[typeStr]['curPos'] += 1
        
        if self.sol != None and varName in self.sol:
            # we have a value! update cache and return it
            newVal = self.sol[varName]
            self.rewriteDict[typeStr]['symbolCache'][fromStr] = newVal
            return newVal
        elif fromStr in self.rewriteDict[typeStr]['symbolCache']:
            return self.rewriteDict[typeStr]['symbolCache'][fromStr]
        else:
            #not found in this type's map in this generation, return original
            return fromStr

    def getShort(self,name):
        if name == self.FUNCNAME:
            return "f"
        elif name == self.VAR:
            return "m"
        elif name == self.REGISTER:
            return "r"
        else :
            raise hell
        
    def getVarName(self,preFix,curLine,curPos):
        return preFix + str(curLine) + "-" + str(curPos) + "_TAR"

    # TODO - make this __
    def callSol(self):
        # we need to go over each dict that is useable, and feed vars and constraints
        for typeDict in [x for x in self.rewriteDict.keys() if self.rewriteDict[x]['useAble']==True ]:
            curLine = 1
            curPos = 1
            
            preFix = self.getShort(typeDict)
            #if typeDict != self.REGISTER:
            domain = list(self.rewriteDict[typeDict]['domain']) 
            #else:
            #    domain =self.__registers32Bit
            for (line,tarStr,refStr) in self.rewriteDict[typeDict]['transitions']:
                if curLine < line:
                    curPos = 1
                    curLine = line
                    
                tarName = self.getVarName(preFix, curLine, curPos)
                
                self.problem.addVariables([tarName],domain)
                if (self.__printConds):
                    print "CONS(text) -> " + tarName + " == " + refStr 
                self.problem.addConstraint(self.checkInputVsTarget(refStr),[tarName])
                
            
                if tarStr in self.rewriteDict[typeDict]['valuesTrackDict'] != None:
                    if (self.__printConds):
                        print "CONS(bag) -> " + self.rewriteDict[typeDict]['valuesTrackDict'][tarStr] + " == " + tarName 
                    self.problem.addConstraint(self.varsEqual,[tarName,self.rewriteDict[typeDict]['valuesTrackDict'][tarStr]])
                self.rewriteDict[typeDict]['valuesTrackDict'][tarStr] = tarName
                        
                curPos+=1
                
        self.sol = self.problem.getSolution()
        if traceHack:
            print "(Number of broken - " + str(self.problem.getSolver().getHack()) + ")",

    def varsEqual(self,v1, v2):
        return v1==v2
    
    def checkInputVsTarget(self,target):
        def retFunc(inputVal):
            return inputVal == target
        
        return retFunc     
    
               
    def getSolution(self):
        if self.sol == None:
            self.callSol()
            
        return self.sol
    
    def printSol(self,sol):
        #better call sol!
        
        if sol == None:
            print "NO SOL!"
            return
        
        last = 1
        for key in sorted(sol.iterkeys()):
            if int(key[1:2]) != last:
                last = int(key[1:2])
                print ""
            
            print key + ": " + sol[key] + " ",
             
    def getBrokenNumber(self):
        return self.problem.getSolver().getHack()


def NodeInfoFromCode(refCmds,tarCmds):
    matched = map(lambda (ref,tar): {'ref':ref,'tar':tar},zip(refCmds,tarCmds))
    for index,record in enumerate(matched):
        record['tarCmdNum'] = index+1
        record['refCmdNum'] = index+1
        
    return {'matchedCmds':matched ,'deletedCmds':[],'insertedCmds':[],'gradesDict':{'ratio':0,'contain':0},'refCode':";".join(refCmds)+";",'tarCode':";".join(tarCmds)+";"}

def selfTest():
    
    refCmds1 = ["MOV eax,ebx" ]
    tarCmds1 = ["MOV ecx,edx" ]
    
    refCmds2 = ["MOV esi,eax" ]
    tarCmds2 = ["MOV edi,ecx" ]
    
    gc = GraphletsConstraints([NodeInfoFromCode(refCmds1,tarCmds1),NodeInfoFromCode(refCmds2,tarCmds2)])
    #gc.callSol()
    #gc.printSol(gc.getSolution())
    for cmds in gc.getRW():
        pass
        #print cmds
        
    """    
    (1)Add ecx,ebx
    (+)Xor ebx,ebx
    (2)Mov [IO],ecx
    (3)Mov ecx,[IO+4] 
    (4)Add eax,ecx  
    
    
    (1) Add ebx,esi
    (2) Mov [ME],ebx
    (X) Lea ebx, [ME8]
    (3) Mov esi,[ME+4]
    (4) Add eax,esi
    
    """

    refCmds1 = ["Add ecx,ebx" ]
    refCmds2 = ["Mov [var_IO],ecx" ]
    refCmds3 = ["Mov ecx,[var_IO+4] " ]
    refCmds4 = ["Add eax,ecx" ]
    
    tarCmds1 = ["Add ebx,esi" ]
    tarCmds2 = ["Mov [var_ME],ebx" ]
    tarCmds3 = ["Mov esi,[var_ME+4]" ]
    tarCmds4 = ["Add eax,esi" ]
    
    gc = GraphletsConstraints([NodeInfoFromCode(refCmds1,tarCmds1),NodeInfoFromCode(refCmds2,tarCmds2),NodeInfoFromCode(refCmds3,tarCmds3),NodeInfoFromCode(refCmds4,tarCmds4)])
    #gc.callSol()
    #gc.printSol(gc.getSolution())
    for cmds in gc.getRW():
        print cmds
    
    """     REF   1  2      TAR  1   2
            ============================
        1:  MOV eax,ebx;    MOV ecx,edx
        2:  MOV esi,eax;    MOV edi,ecx
    """
    
    """
    gc = GraphletsConstraints()
    gc.addNewReg(1, 1, "eax", "ecx")
    gc.addNewReg(1, 2, "ebx", "edx")
    
    gc.addNewReg(2, 1, "esi", "edi")
    gc.addNewReg(2, 2, "eax", "ecx")
    
    sol = gc.getSolution()
    #gc.printSol(sol)
    """
    
    """     REF   1  2      TAR  1   2
            ============================
        1:  MOV eax,ebx;    MOV ecx,edx
        2:  MOV ecx,eax;    MOV edi,ecx
        3:  MOV edx,eax;    MOV eax,ecx
        4:  MOV esi,edx;    MOV edi,ecx
        
        ecx -> eax
        edx -> ebx
        edi -> ecx
        eax -> edx
        edi -> esi
        ecx -> edx
        
        
    """
    """
    gc = GraphletsConstraints()
    gc.addNewReg(1, 1, "eax", "ecx")
    gc.addNewReg(1, 2, "ebx", "edx")
    
    gc.addNewReg(2, 1, "ecx", "edi")
    gc.addNewReg(2, 2, "eax", "ecx")
    
    gc.addNewReg(3, 1, "edx", "eax")
    gc.addNewReg(3, 2, "eax", "ecx")
    
    gc.addNewReg(4, 1, "esi", "edi")
    gc.addNewReg(4, 2, "edx", "ecx")
    
    #gc.addNewReg(5, 1, "edi", "esi")
    #gc.addNewReg(5, 2, "eax", "ecx")
    
    sol = gc.getSolution()
    #gc.printSol(sol)
    """
    """     REF   1  2      TAR  1   2
            ============================
        1:  MOV eax,ebx;    MOV ecx,edx
        2:  MOV ecx,eax;    MOV edi,ecx
        3:  MOV edx,eax;    MOV eax,ecx
        4:  MOV esi,edx;    MOV edi,ecx
        5:  MOV edi,eax     MOV esi,ecx
    
        ecx -> eax (4)  - 1
        edx -> ebx
        edi -> ecx (2)
        eax -> edx
        esi -> edi
        
    """
    """
    gc = GraphletsConstraints()
    gc.addNewReg(1, 1, "eax", "ecx")
    gc.addNewReg(1, 2, "ebx", "edx")
    
    gc.addNewReg(2, 1, "ecx", "edi")
    gc.addNewReg(2, 2, "eax", "ecx")
    
    gc.addNewReg(3, 1, "edx", "eax")
    gc.addNewReg(3, 2, "eax", "ecx")
    
    gc.addNewReg(4, 1, "esi", "edi")
    gc.addNewReg(4, 2, "edx", "ecx")
    
    gc.addNewReg(5, 1, "edi", "esi")
    gc.addNewReg(5, 2, "eax", "ecx")
    
    sol = gc.getSolution()
    gc.printSol(sol)
    """
    
if __name__ == '__main__':   
    selfTest()


#
"""
problem = Problem(MinConflictsSolver())
vars = ["a", "b","c"]

problem.addVariables(vars, [1, 2, 3])


problem.addConstraint(lambda x,y: y> x, ["a","b"])
problem.addConstraint(lambda x,y: y> x, ["a","c"])
problem.addConstraint(lambda x,y: y> x, ["b","c"])
problem.addConstraint(lambda a: a> 1, ["a"])

problem.addConstraint(check, ["c"])

problem.addConstraint(lambda b: b <3, ["b"])
problem.addConstraint(lambda a,b: a != b, ["a","b"])
problem.addConstraint(lambda a,c: a != c, ["a","c"])

 
print problem.getSolution()
"""
