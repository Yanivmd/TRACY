import itertools

from constraint import Problem,MinConflictsSolver

from x86Analyzer import RWEngineBase,isCall,isRegisterStr,isVarStr,isOffset,seperateCmd

class GraphletsConstraints(RWEngineBase):
    
    __printConds = False
    
    def __init__(self,nodeGradesInfos):
        self.nodeGradesInfos = nodeGradesInfos
        self.sol = None
    
    
    # a field is somthing seperated by " " , an argument is a list of params seperated by "," ; a member is a param seperated by "+"
    def breakCommand(self,cmd):
        cmdFields = seperateCmd(cmd)
        if len(cmdFields) ==0:
            print "asd"
        assert (len(cmdFields) >0)
        if len(cmdFields) == 1 :
            return {'nemonic':cmdFields[0],'nemonicWithDecoretors':" ".join(cmdFields[0:-1]),'ParamsList':[]}
        else:
            return {'nemonic':cmdFields[0],'nemonicWithDecoretors':" ".join(cmdFields[0:-1]),'ParamsList':cmdFields[-1].split(",")}
    
    
    #TODO - add to this..
    lvalCmdsStarts = ["mov","sub","add","xor"]
    
    def getNemonicType(self,nemonic):
        if any(map(lambda startString: nemonic.startswith(startString),self.lvalCmdsStarts)):
            return "WriteThenRead"
        else:
            return "Read"
    
    FuncPrefix = "f"
    VARPrefix = "s"
    RegisterPrefix = "r"
    OffsetPrefix = "o"
    OtherPrefix = "X"
    
    def getPrefix(self,Str):
        if isVarStr(Str):
            return self.VARPrefix
        elif isRegisterStr(Str):
            return self.RegisterPrefix
        elif isOffset(Str):
            return self.OffsetPrefix
        else:
            return self.OtherPrefix 
            

    def varsEqual(self,v1, v2):
        return v1==v2
    
    def checkInputVsTarget(self,target):
        def retFunc(inputVal):
            return inputVal == target
        
        return retFunc     


    def getVarName(self,prefix,lineNumber,varsInThisLine):
        return prefix + str(lineNumber) + "-" + str(varsInThisLine) + "_TAR"

    def getMembers(self,param):
        refMembers = param.split("+")
        refMembers[0] = refMembers[0][1:] #remove [ from first
        refMembers[-1] = refMembers[-1][0:-1]  # remove ] from last (they can be the same one!)
        return refMembers

    def getDomains(self):
        domains = {self.FuncPrefix:set(),self.VARPrefix:set(),self.RegisterPrefix:set(),self.OffsetPrefix:set()}
        
        def getCmdSymbols(cmd):
            cmdBasicInfo = self.breakCommand(cmd)
            for param in cmdBasicInfo['ParamsList']:
                if param.startswith("["):
                    for member in self.getMembers(param):
                        yield member
                else:
                    yield param
        
        def getCmds(cmdsDelimited):
            return filter(None,cmdsDelimited.split(";"))
        
        for cmdList in itertools.imap(lambda nodeGradesInfo:getCmds(nodeGradesInfo['refCode']),self.nodeGradesInfos):
            for cmd in cmdList:
                
                if isCall(cmd):
                    prefix = self.FuncPrefix
                    domains[prefix].add(list(getCmdSymbols(cmd))[0])
                else:
                    for symbol in getCmdSymbols(cmd):
                        prefix = self.getPrefix(symbol)
                        if prefix != self.OtherPrefix:
                            domains[prefix].add(symbol)
            
        for domainName in domains.keys():
            domains[domainName] = list(domains[domainName])
            
        return domains

    def callSol(self):
        
        
        domains = self.getDomains()
        
        #domains[refPrefix].add(refVal) 
        
        self.problem = Problem(MinConflictsSolver())
        
        tarSymbolsCache = {}
        
        self.varsInThisLine = 0
        
        def addInTraceletCons(tarVal,newVarName):
            if (self.__printConds):
                print "CONS(IN) -> " + tarSymbolsCache[tarVal] + " == " + newVarName 
            self.problem.addConstraint(self.varsEqual,[newVarName,tarSymbolsCache[tarVal]])
            
            
        def addCrossTraceletCons(refVal,newVarName,refPrefix):
            if (self.__printConds):
                print "CONS(CROSS) -> " + newVarName + " == " + refVal
            self.problem.addConstraint(self.checkInputVsTarget(refVal),[newVarName])
        
        
        def addVarWithPrefix(prefix,lineNumber):
            newVarName = self.getVarName(prefix,lineNumber,self.varsInThisLine)
            if len(domains[prefix]) == 0:
                print "EMP"
            self.problem.addVariables([newVarName],domains[prefix])
            self.varsInThisLine+=1
            return newVarName
        
        
        # mode can be - WRITE or NORMAL
        def doDF(refSymbol,tarSymbol,lineNumber,refPrefix,tarPrefix,nemonicType):
            
            if refPrefix == self.OtherPrefix or tarPrefix == self.OtherPrefix:
                return 
            
            newVarName = addVarWithPrefix(tarPrefix,lineNumber)
            
            if (refPrefix == tarPrefix):
                addCrossTraceletCons(refSymbol,newVarName,refPrefix)
        
            if tarSymbol in tarSymbolsCache:  
                addInTraceletCons(tarSymbol,newVarName)
                
            if tarPrefix != self.RegisterPrefix or nemonicType=="WriteThenRead":
                tarSymbolsCache[tarSymbol] = newVarName
        
        
        #for matchedCmd in itertools.chain(map(lambda nodeInfo:nodeInfo['matchedCmds'],self.nodeGradesInfos)):
        
        tarBase = 0
        refBase = 0
        
        for nodeInfo in self.nodeGradesInfos:
            for matchedCmd in nodeInfo['matchedCmds']:
                
                self.varsInThisLine = 1
        
                # if these cmds are not an operational match, we cannot cross tracelet match them.
                if matchedCmd['operationMatch'] == True:
                    
                    currentLineNumber = tarBase + matchedCmd['tarCmdNum'] #  matchedCmd['tarCmdNum'] is 1 based so we are ok
                    
                    if matchedCmd['tar'] =="" or matchedCmd['ref'] =="":
                        continue
                    
                    tarCmdBasicInfo = self.breakCommand(matchedCmd['tar'])
                    refCmdBasicInfo = self.breakCommand(matchedCmd['ref'])
                    if len(tarCmdBasicInfo['ParamsList'])>0 and len(refCmdBasicInfo['ParamsList'])>0:
                        
                        if tarCmdBasicInfo['nemonic'] == 'call':
                            
                            assert(len(refCmdBasicInfo['ParamsList'])==1)
                            assert(len(tarCmdBasicInfo['ParamsList'])==1)
                            
                            doDF(refCmdBasicInfo['ParamsList'][0], tarCmdBasicInfo['ParamsList'][0], currentLineNumber, self.FuncPrefix,self.FuncPrefix, "Read")
                        else:
                        
                            nemonicType = self.getNemonicType(tarCmdBasicInfo['nemonic'])
                            
                            for (refParam,tarParam) in zip(refCmdBasicInfo['ParamsList'],tarCmdBasicInfo['ParamsList']):
                                
                                tarIsMem = "[" in tarParam
                                if tarIsMem != ("[" in refParam):
                                    continue
                                    print matchedCmd
                                    print "BOY"
                                
                                assert  tarIsMem == ("[" in refParam)
                                
                                if not tarIsMem:
                                    tarPreFix = self.getPrefix(tarParam)
                                    refPreFix = self.getPrefix(refParam)
                                    
                                    doDF(refParam, tarParam, currentLineNumber, tarPreFix,refPreFix, nemonicType)
                                      
                                      
                                    # TODO - return this to find more classes when we have time...
                                    """
                                    if nemonicType == "WriteThenRead":  
                                        if tarPreFix != self.RegisterPrefix:
                                            print matchedCmd
                                        
                                        assert (tarPreFix == self.RegisterPrefix)
                                        # the write is only to the left most param, rest are normal
                                    """
                                else:
                                    # this is memory! , first remove '[',']'
    
                                    for (refMember,tarMember) in zip(self.getMembers(refParam),self.getMembers(tarParam)):
                                        tarPreFix = self.getPrefix(tarMember)
                                        refPreFix = self.getPrefix(refMember)
                                        doDF(refMember, tarMember, currentLineNumber, tarPreFix,refPreFix, nemonicType)
                                        
                                nemonicType = "Read"
                                        
                                        
                    #TODO handle the False clause ?
                     
            tarBase += nodeInfo['tarCode'].count(";")
            refBase += nodeInfo['refCode'].count(";")
                    
                   
            
        self.sol = self.problem.getSolution()
        
        #print self.sol
    
    def getBrokenNumber(self):
        return self.problem.getSolver().getHack()
    
    # TODO - make this __
    def getRW(self):
        sol = self.getSolution()
        
        tarBase = 0
               
        symbolsCache = {}
        
        self.varsInThisLine = 0
        TotalLineNumber = 0
        
        def getRewrittenSymbolUpdateCache(prefix,symbol):
            varName = self.getVarName(prefix, TotalLineNumber, self.varsInThisLine)
            if sol != None and varName in sol:
                symbolsCache[symbol] = sol[varName]
                return sol[varName]
            else:
                return symbol
        
        def rewrittenParam(param):
            if param.startswith("["):
                rewrittenMembers = []
                for member in self.getMembers(param):
                    rewrittenMembers.append(getRewrittenSymbolUpdateCache(self.getPrefix(member), member))
                    self.varsInThisLine+=1
                return "[" + "+".join(rewrittenMembers) + "]"
            else:
                newParam = getRewrittenSymbolUpdateCache(self.getPrefix(param), param)
                self.varsInThisLine+=1
                return newParam
               
        
        for nodeInfo in self.nodeGradesInfos:
        
            cmdsStr = nodeInfo['tarCode']
            rewrittenCmds = []
    
            lastLineNumber = 0 #filter(None,)
            for (lineNumber,cmd) in enumerate(cmdsStr.split(";")):
                
                TotalLineNumber = tarBase + lineNumber + 1 # we are one based
                lastLineNumber = lineNumber +1  # we are one based
                
                self.varsInThisLine = 1
                
                if cmd != "":
                    tarCmdBasicInfo = self.breakCommand(cmd)
                    if len(tarCmdBasicInfo['ParamsList'])>0:
                        if tarCmdBasicInfo['nemonic'] == 'call':
                            rewrittenCmds.append("call " + getRewrittenSymbolUpdateCache(self.FuncPrefix,tarCmdBasicInfo['ParamsList'][0]))
                        else:
                            rewrittenCmds.append(tarCmdBasicInfo['nemonicWithDecoretors'] + " " + ",".join(map(rewrittenParam,tarCmdBasicInfo['ParamsList'])))
                    else:
                        rewrittenCmds.append(cmd)
                else:
                    # this mostly cuz of bugs, but if i wont accumidate them it will cause a bad grade for nothing..(everything else wont be aligned)
                    rewrittenCmds.append(cmd)
            
            tarBase += lastLineNumber-1
    
            yield ";".join(rewrittenCmds)
        
        
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


def NodeInfoFromCode(refCmds,tarCmds):
    
    matched=[]
    for (index,(ref,tar)) in enumerate(zip(refCmds,tarCmds)):
        matched.append({'ref':ref,'tar':tar,'tarCmdNum':index,'refCmdNum':index,'operationMatch':True})
    for index,record in enumerate(matched):
        record['tarCmdNum'] = index+1
        record['refCmdNum'] = index+1
        
    return {'matchedCmds':matched ,'deletedCmds':[],'insertedCmds':[],'gradesDict':{'ratio':0,'contain':0},'refCode':";".join(refCmds)+";",'tarCode':";".join(tarCmds)+";"}

def selfTest():
    
    print "!!!TEST 1!!!!"
    
    refCmds1 = ["mov eax,ebx" ]
    refCmds2 = ["mov esi,eax" ]
    
    tarCmds1 = ["mov ecx,edx" ]
    tarCmds2 = ["mov edi,ecx" ]
    
    gc = GraphletsConstraints([NodeInfoFromCode(refCmds1,tarCmds1),NodeInfoFromCode(refCmds2,tarCmds2)])
    #gc.callSol()
    #gc.printSol(gc.getSolution())
    for cmds in gc.getRW():
        pass
        #print cmds
        
    """    REF:
    (1)Add ecx,ebx
    (+)Xor ebx,ebx
    (2)Mov [var_IO],ecx
    (3)Mov ecx,[var_IO+4] 
    (4)Add eax,ecx  
    
           TAR:
    (1) Add ebx,esi
    (2) Mov [var_ME],ebx
    (X) Lea ebx, [var_ME8]
    (3) Mov esi,[var_ME+4]
    (4) Add eax,esi
    
    """

    print "!!!TEST 2!!!!"

    refCmds1 = ["add ecx,ebx" ]
    refCmds2 = ["mov [var_IO],ecx" ]
    refCmds3 = ["mov ecx,[var_IO+4] " ]
    refCmds4 = ["add eax,ecx" ]
    
    tarCmds1 = ["add ebx,esi" ]
    tarCmds2 = ["mov [var_ME],ebx" ]
    tarCmds3 = ["mov esi,[var_ME+4]" ]
    tarCmds4 = ["add eax,esi" ]
    
    gc = GraphletsConstraints([NodeInfoFromCode(refCmds1,tarCmds1),NodeInfoFromCode(refCmds2,tarCmds2),NodeInfoFromCode(refCmds3,tarCmds3),NodeInfoFromCode(refCmds4,tarCmds4)])
    
    #gc.callSol()
    #gc.printSol(gc.getSolution())
    headNotPrinted = True
    for cmds in gc.getRW():
        if headNotPrinted:
            print "!!!TEST 2 - RW result!!!!"
            headNotPrinted = False
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
