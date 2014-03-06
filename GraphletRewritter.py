#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      user
#
# Created:     17/08/2013
# Copyright:   (c) user 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python



import itertools


from x86Analyzer import X86AnalyzerBase

class RWDict(X86AnalyzerBase):

    
    # this gets MatchedCmds tuple, (rest = target (tarStr) and reference (refStr) , for debug)
    def __init__(self,nodeGradesInfos=[]):
        X86AnalyzerBase.__init__(self,nodeGradesInfos)
        
        self.createRewrite()
        self.__createBlackList()
       

    def getEmptyDict(self):
        d = X86AnalyzerBase.getEmptyDict(self)
        for key in d.keys():
            d[key]['entries'] = {}
            
        return d
    
    def commitChanges(self,tmpDict):
        self.__mergeDictIntoSelf(tmpDict)
        
        # this will add recorded value to dict, even if there is a conflict it will be recorded...
    #
    def insertToDictWithType(self,tarCmdNum,fromStr,refCmdNum,toStr,typeStr,dict2insert=None):
        #if dict2insert == None:
        dict2insert = self.rewriteDict

        #(yo dawg i heard u like dicts...:\ the value is a counter)

        if not dict2insert[typeStr]['entries'].has_key(fromStr):
            dict2insert[typeStr]['entries'][fromStr] = {'values':dict(),'generation':self.generation}

        if dict2insert[typeStr]['entries'][fromStr]['values'].has_key(toStr):
            dict2insert[typeStr]['entries'][fromStr]['values'][toStr] += 1
        else:
            dict2insert[typeStr]['entries'][fromStr]['values'][toStr] = 1


    # black list has no generation:) , we can use the rwdict type as they are the same..
    def getRewriteWithType(self,tarCmdNum,fromStr,typeStr,FoundBlacklistElement):
        if self.BlacklistDict[typeStr]['entries'].has_key(fromStr):
            FoundBlacklistElement[0] = True

        elif self.rewriteDict[typeStr]['entries'].has_key(fromStr):
            if self.rewriteDict[typeStr]['entries'][fromStr]['generation'] == self.generation:
                if len(self.rewriteDict[typeStr]['entries'][fromStr]['values']) == 1:
                    return self.rewriteDict[typeStr]['entries'][fromStr]['values'].keys()[0]
                else:
                    # we are in conflict, return original
                    return fromStr

        #not found in this type's map in this generation, return original
        return fromStr

    def incGeneration(self):
        self.generation += 1

    # this will check our dict and make sure atleast one "real" entry is there
    def isMeaningfull(self):
        for typeStr in self.rewriteDict.keys():
            for entry in self.rewriteDict[typeStr]['entries'].keys():
                if len(self.rewriteDict[typeStr]['entries'][entry]['values']) == 1 and self.rewriteDict[typeStr]['entries'][entry]['values'].keys()[0] != entry :
                    return True

    # this will merge 'other' into self, only iff there are no conflicts
    def mergeIntoSelf(self,other):
        self.__mergeDictIntoSelf(other.rewriteDict)


    # this will merge 'other' into self, only iff there are no conflicts
    def __mergeDictIntoSelf(self,otherDict):
        myDict = self.rewriteDict
        for typeStr in [x for x in myDict.keys() if myDict[x]['Mergeable']==True ]:
            for entry in otherDict[typeStr]['entries'].keys():
                if myDict[typeStr]['entries'].has_key(entry):
                    for value in otherDict[typeStr]['entries'][entry]['values']:
                        if myDict[typeStr]['entries'][entry]['values'].has_key(value):
                            myDict[typeStr]['entries'][entry]['values'][value] += otherDict[typeStr]['entries'][entry]['values'][value]
                        else:
                            myDict[typeStr]['entries'][entry]['values'][value] = otherDict[typeStr]['entries'][entry]['values'][value]
                else:
                    self.rewriteDict[typeStr]['entries'][entry] = otherDict[typeStr]['entries'][entry].copy()

    def __getDictAsString(self,myDict):
        outStr = []
        out = ""
        for typeStr in myDict.keys():
            typePrinted = False

            for entry in myDict[typeStr]['entries'].keys():
                if len(myDict[typeStr]['entries'][entry]['values']) == 1:
                    if myDict[typeStr]['entries'][entry]['values'].keys()[0] != entry :
                        if not typePrinted:
                            out += "TYPE={" + typeStr + "}-"
                            typePrinted = True
                        outStr.append(entry + " -> " + myDict[typeStr]['entries'][entry]['values'].keys()[0])
                else:
                    if not typePrinted:
                        out += "TYPE={" + typeStr + "}-"
                        typePrinted = True
                    outStr.append ( entry + " -> *Conflict*")
            out += ",".join(outStr)
            if typePrinted:
                out += "|"
            outStr = []

        return out;

    # our print is the dict print..
    def __str__(self):
        return "Dict:" + self.__getDictAsString(self.rewriteDict) + " *** BlackList:" + self.__getDictAsString(self.BlacklistDict)

        #return out

    """
    # this will add recorded value to dict, even if there is a conflict it will be recorded...
    def __insertToBlackList(self,Str,typeStr):

        if not self.BlacklistDict[typeStr]['entries'].has_key(Str):
            self.BlacklistDict[typeStr]['entries'][Str] = 1
        else:
            self.BlacklistDict[typeStr]['entries'][Str] += 1
    """

    def __createBlackList(self):

        for nodeInfo in self.nodeGradesInfos:
            
            cmds = nodeInfo['deletedCmds']
    
            def getCmdParams(cmd):
                spParams = cmd.split(" ")
                spParams.pop(0)
                if len(spParams) > 0:
                    comParams = list(itertools.chain(*map(lambda x: x.split(","),spParams)))
                    return list(itertools.chain(*map(lambda x: x[1:-1].split("+") if x.startswith("[") else x.split("+"),comParams)))
                else:
                    return spParams
    
            for cmd in cmds:
                if cmd != "":
                    # we only support var ban for now...
                    cmdParams = getCmdParams(cmd)
                    for param in cmdParams:
                        if self.BlacklistDict[self.VAR]['testerFunction'](param):
                            self.insertToDictWithType(-1,param,-1,param,self.VAR,self.BlacklistDict)


    
