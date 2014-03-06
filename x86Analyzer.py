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



import difflib

import inspect

import myutils

import itertools

import logging
import sys



def seperateCmd(cmd):
    cmdFields = filter(None,cmd.split(" "))
    
    if len(cmdFields) >= 3:
        if "," in cmdFields[-2]:
            #print cmd
            
            #if "mov" in cmd:
            #    if cmd.count("mov") > 1:
            #        print "too much in one cmd:" + cmd
            #        assert(False)
            
            last = cmdFields[-1]
            cmdFields = cmdFields[0:-1]
            cmdFields[-1] += " " + last
            
    return cmdFields


def isRegisterStr(Str):
    
    # the s: is a really nasty hack to get "ds:DWORD" and "cs:DWORD" to count as r
    #"s:"
    Registers = ["ax","bx","cx","dx","si","di","bp","sp"]
    return Str in Registers or Str[1:] in Registers

def isVarStr(Str):
    return Str.startswith("var_")

def isOffset(Str):
    return Str.startswith("offset") or Str.startswith("(offset")

def isCall(cmdStr):
    return cmdStr.startswith("call ")

def alwaysTrue(x):
    return True


class RWEngineBase():
    def getRW(self):
        raise NotImplementedError('This method must be overriden')

class X86AnalyzerBase(RWEngineBase):

    printMatchedCmds = False
    printCmdMatchErrors = False

    FUNCNAME = "FunctionNames"
    REGISTER = "Registers"
    VAR = "Var"
    OTHER = "Other"

    def getEmptyDict(self):
        # this will be the dict of cmds type
        rewriteDict = dict()
        rewriteDict[self.FUNCNAME] = ({'testerFunction':alwaysTrue,'Mergeable':True,'isArgument':False,'useAble':True})
        rewriteDict[self.REGISTER] = ({'testerFunction':isRegisterStr,'Mergeable':False,'isArgument':True,'useAble':True})
        rewriteDict[self.VAR] = ({'testerFunction': isVarStr,'Mergeable':True,'isArgument':True,'useAble':True})
        rewriteDict[self.OTHER] = ({'testerFunction': alwaysTrue,'Mergeable':True,'isArgument':True,'useAble':False})
        
        return rewriteDict

    # this gets MatchedCmds tuple, (rest = target (tarStr) and reference (refStr) , for debug)
    def __init__(self,nodeGradesInfos=[]):
        
        self.rewriteDict = self.getEmptyDict()
        self.BlacklistDict = self.getEmptyDict()
        self.generation = 0

        self.nodeGradesInfos = nodeGradesInfos

        if len(nodeGradesInfos)==0:
            return
            
        if (self.printMatchedCmds):
            # TODO fix this with chain..
            raise hell
            for match in self.matchedCmds:
                print match


    # this will add recorded value to dict, even if there is a conflict it will be recorded...
    def insertToDictWithType(self,tarCmdNum,fromStr,refCmdNum,toStr,typeStr,dict2insert=None):
        raise NotImplementedError('This method must be overriden')

    def __insertToDict(self,tarCmdNum,fromStr,refCmdNum,toStr,dict2insert=None):
        if dict2insert == None:
            dict2insert = self.rewriteDict

        for typeDict in [x for x in dict2insert.keys() if dict2insert[x]['isArgument']==True ]:
            res = myutils.iff(dict2insert[typeDict]['testerFunction'],fromStr,toStr)
            if res < 0:
                return

            if res == 1:
                self.insertToDictWithType(tarCmdNum,fromStr,refCmdNum,toStr,typeDict,dict2insert)
                return

            if res == 0:
                continue
           

    # the ref and tar are needed here only for debug - to present the context the cmd was extracted from
    def createRewrite(self):
        
        tarBase = 0
        refBase = 0
        
        for nodeInfo in self.nodeGradesInfos:
            for cmd in nodeInfo['matchedCmds']:
                
                tarCmdNum = tarBase + cmd['tarCmdNum']
                refCmdNum = refBase + cmd['refCmdNum']
                
                #ref = self.refCode
                #tar = self.tarCode
                
                res = myutils.iff(isCall,cmd['ref'],cmd['tar'])
                if res < 0:
                    if self.printCmdMatchErrors:
                        print "bad command match" + "(refcmd=" + cmd['ref'] + ",tarcmd=" + cmd['tar'] + ")"
                    continue
                elif res == 1:
                    self.insertToDictWithType(tarCmdNum,cmd['tar'][len("call "):],refCmdNum,cmd['ref'][len("call "):],self.FUNCNAME,self.rewriteDict)
                    continue
    
                res = myutils.iff(lambda x: x.startswith("<"),cmd['ref'],cmd['tar'])
                if res < 0:
                    if self.printCmdMatchErrors:
                        print "bad command match"
                    continue
                elif res == 1:
                    continue # we do nothing with this now...
                else:
    
                    tmpDict = self.getEmptyDict()
    
                    cmdPartsRef = cmd['ref'].split(" ")
                    cmdPartsTar = cmd['tar'].split(" ")
    
                    if cmdPartsRef[0] != cmdPartsTar[0]:
                        if self.printCmdMatchErrors:
                            print "bad command match" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                        continue
    
                    if len(cmdPartsRef) != len(cmdPartsTar):
                        if self.printCmdMatchErrors:
                            print "bad command match in cmd parts" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                        continue
    
                    for i in range(1,len(cmdPartsRef)):
    
                        res = myutils.iff(lambda x: x != "",cmdPartsRef[i],cmdPartsTar[i])
                        if res < 0:
                            if self.printCmdMatchErrors:
                                print "bad command match in cmd parts one empty one not" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                            continue
                            #no args, nothing to learn here.
    
                        if res==0:
                            if self.printCmdMatchErrors:
                                print "two empty commands" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                            continue
    
                        #else they are both not empty
    
                        argsRef = cmdPartsRef[i].split(",")
                        argsTar = cmdPartsTar[i].split(",")
    
                        if len(argsRef) != len(argsTar):
                            if self.printCmdMatchErrors:
                                print "bad command match in args" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                            continue
    
                        for j in range(0,len(argsRef)):
                            res = myutils.iff(lambda x: x.startswith("[") and x.endswith("]"),argsRef[j],argsTar[j])
                            if res < 0 :
                                if self.printCmdMatchErrors:
                                    print "bad command match in args one mem one not" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                                continue
    
                            elif res == 1:
                                #both mem operations
                                singleArgRef = argsRef[j][1:-1]
                                singleArgTar = argsTar[j][1:-1]
    
                                paramsRef = singleArgRef.split("+")
                                paramsTar = singleArgTar.split("+")
    
                                if len(paramsRef) == len(paramsTar):
                                    for k in range(0,len(paramsRef)):
                                        self.__insertToDict(tarCmdNum,paramsTar[k],refCmdNum,paramsRef[k],tmpDict)
    
                                else:
                                    if self.printCmdMatchErrors:
                                        print "bad command match - number of params is not the same" + "(ref=" + cmd['ref'] + ",tar=" + cmd['tar'] + ")"
                                    continue
    
    
                            else:
                                #both without mem
                                self.__insertToDict(tarCmdNum,argsTar[j],refCmdNum,argsRef[j],tmpDict)
    
                    # we passed the parameted\argument compare and the cmds have the same structure. we commit the changes.
                    self.commitChanges(tmpDict)
                    
            tarBase += nodeInfo['tarCode'].count(";")
            refBase += nodeInfo['refCode'].count(";")
                
    def commitChanges(self,tmpDict):
        raise NotImplementedError('This method must be overriden')

    #returns a rewrite or the original str if not found or conflict.
    def getRewriteWithType(self,tarCmdNum,fromStr,typeStr,FoundBlacklistElement):
        raise NotImplementedError('This method must be overriden')

    #returns a rewrite or the original str if not found or conflict.
    def __getRewrite(self,tarCmdNum,fromStr,FoundBlacklistElement):
        for typeDict in [x for x in self.rewriteDict.keys() if self.rewriteDict[x]['isArgument']==True and self.rewriteDict[x]['useAble']==True ]:
            if not self.rewriteDict[typeDict]['testerFunction'](fromStr):
                continue
            return self.getRewriteWithType(tarCmdNum,fromStr,typeDict,FoundBlacklistElement)

        # no match for any type, return original
        return fromStr


    def getRW(self):
        
        tarBase = 0
        for nodeInfo in self.nodeGradesInfos:
        
            cmdsStr = nodeInfo['tarCode']
            rewrittenCmds = []
    
            for lineNumber,cmd in enumerate(cmdsStr.split(";")):
    
                tarCmdNum = tarBase + lineNumber + 1
    
                FoundBlacklistElement = [False]
    
                if cmd.startswith("<"):
                    #this is a goto cmd - TODO
                    rewrittenCmds.append(cmd)
    
                elif cmd.startswith("call "):
                    #this is a call cmd - TODO
                    rewrittenCmds.append("call " + self.getRewriteWithType(tarCmdNum,cmd[len("call "):],self.FUNCNAME,FoundBlacklistElement))
    
                else:
                    cmdParts = cmd.split(" ")
                    rewrittenCmdParts = []
    
                    #opcode will not be changed...
                    rewrittenCmdParts.append(cmdParts[0])
    
                    for i in range(1,len(cmdParts)):
    
                        if cmdParts[i] == "":
                            raise hell
    
                        args = cmdParts[i].split(",")
                        rewrittenArgs = []
    
                        for j in range(0,len(args)):
                            if args[j].startswith("[") and args[j].endswith("]"):
    
                                # mem operations
                                singleArg = args[j][1:-1]
    
                                params = singleArg.split("+")
                                rewrittenParams = []
    
                                for k in range(0,len(params)):
                                    rewrittenParams.append(self.__getRewrite(tarCmdNum,params[k],FoundBlacklistElement))
    
                                rewrittenArgs.append("[" + "+".join(rewrittenParams) + "]")
    
                            else:
                                # without mem
                                rewrittenArgs.append(self.__getRewrite(tarCmdNum,args[j],FoundBlacklistElement))
    
    
                        rewrittenCmdParts.append(','.join(rewrittenArgs))
    
                    if FoundBlacklistElement[0] == False:
                        rewrittenCmds.append(' '.join(rewrittenCmdParts))
                        
            tarBase += nodeInfo['tarCode'].count(";")
    
            yield ";".join(rewrittenCmds)

            


            