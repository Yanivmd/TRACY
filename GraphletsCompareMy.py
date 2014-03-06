#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      user
#
# Created:     22/08/2013
# Copyright:   (c) user 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from difflib import *

import myutils

import numpy

#this is needed only for tests...
import GraphletRewritter

printTrace = False

"""
    we name the intel x86 cmd layout as written by IDA:
    <OPCODE + describers> <param1><param2>

    example for describers:
    mov ptr byte VS just mov

    we grade cmd match with this logic:
        if opcode is exactly the same (OPCODE + describers) +2
            if opcode is partly the same - +1

        if first param same  - +1
        if sec param is same -  +1

    if something is "missing" we dont give it points (params etc..)

"""

def __calcMaxCmdsGrade(refCmds):
    return sum(map(lambda x:__gradeCmdMatch(x,x),refCmds))



def __gradeCmdMatch(refCmd,tarCmd):

    if refCmd == "" or tarCmd == "":
        return 0

    totalGrade = 0

    refFields = refCmd.split(" ")
    tarFields = tarCmd.split(" ")

    refParams = refFields[-1].split(",")
    tarParams = tarFields[-1].split(",")


    #sanity - no cmd with 3 params
    # TODO - remove
    res = myutils.iff(lambda x: len(x) < 3,refParams,tarParams)
    if res != 1:
        print "REF=" + str(refCmd)
        print "TAR=" + str(tarCmd)
        raise hell
        

    # if we dont have the same ammount of params this means we dont have the same opcode.. 
    # we just give this 0!
    if len(refParams) == len(tarParams):
        #refParams = [refFields[-1]]
        #tarParams = [tarFields[-1]]

        for i in range(0,len(refParams)):
            if refParams[i] == tarParams[i]:
                totalGrade += 1

        if refFields[0] == tarFields[0]:
            totalGrade += 1

        if refFields[1:-1] == tarFields[1:-1] and refFields[1:-1] != []:
            totalGrade += 1

    return totalGrade



# this will return (matchedCmds,deletedCmds,insertedCmds,grade)
# deleted is cmds we need to delete from tar (left overs not matched from tar)
# insert are cmds we need to insert into ref (left overs not matched in ref)
def __doGetMatchedCmds(refCmds,tarCmds,fillArrays=True):

    res = myutils.iff(lambda x: x == [],refCmds, tarCmds) 
    if res == 1:
        return ([],[],[],0)
    elif res < 0:
        return ([],tarCmds,[],0) if res == -1 else ([],[],refCmds,0)

    # we have tarCmds rows, and refCmds columns
    # where ar[0][1] is row 0 col 1
    array = []
    for i in range(0,len(tarCmds)):
        array.append([0] * len(refCmds))

    #fill last row
    for i in range(0,len(refCmds)):
        grade = __gradeCmdMatch(refCmds[i],tarCmds[-1])
        array[-1][i] = {'my':grade,'best':grade}

    # fill last column
    for i in range(0,len(tarCmds)):
        grade = __gradeCmdMatch(refCmds[-1],tarCmds[i])
        array[i][-1] = {'my':grade,'best':grade}

    # work on the rest of them
    for i in range(len(tarCmds)-2,-1,-1):
        for j in range(len(refCmds)-2,-1,-1):
            grade = __gradeCmdMatch(refCmds[j],tarCmds[i]) + array[i+1][j+1]['best']
            myMax = max(grade,array[i][j+1]['best'],array[i+1][j]['best'])
            array[i][j] = {'my':grade,'best':myMax}

    if fillArrays == False:
        return array[0][0]['best']

    #now we must walk on the array and find the used sequence
    curI = 0
    curJ = 0
    matchedCmds = []
    insertedCmds = []
    deletedCmds = []

    Iok = curI < len(tarCmds)
    Jok = curJ < len(refCmds)

    while Iok and Jok:
        if Iok and Jok and array[curI][curJ]['best'] == array[curI][curJ]['my']:
            # the current one was chosen , +1 cuz here we are 0 based but i want to be 1 based
            matchedCmds.append({'ref':refCmds[curJ],'tar':tarCmds[curI],'tarCmdNum':curI+1,'refCmdNum':curJ+1})
            curI+=1
            Iok = curI < len(tarCmds)
            curJ+=1
            Jok = curJ < len(refCmds)

        elif Jok and array[curI][curJ]['best'] == array[curI][curJ+1]['best']:
            insertedCmds.append(refCmds[curJ])
            curJ+=1
            Jok = curJ < len(refCmds)-1

        elif Iok:
            deletedCmds.append(tarCmds[curI])
            curI+=1
            Iok = curI < len(tarCmds)-1

    while Iok:
        deletedCmds.append(tarCmds[curI])
        curI+=1
        Iok = curI < len(tarCmds)-1

    while Jok:
        insertedCmds.append(refCmds[curJ])
        curJ+=1
        Jok = curJ < len(refCmds)-1


    return (matchedCmds,deletedCmds,insertedCmds,array[0][0]['best'])




def __getGradesDict(grade,refCmds,tarCmds):
    maxRef = __calcMaxCmdsGrade(refCmds)
    maxTar = __calcMaxCmdsGrade(tarCmds)
    containment =   (float(grade) / min(float(maxRef),float(maxTar))) * 100
    ratio  =  (float(grade)*2.0 / float((maxRef+maxTar))) * 100 
    return {'ratio':ratio,'contain':containment}

# the next functions uses my method to grade graphlet match and get matched cmds
#  return (matchedCmds,deletedCmds,insertedCmds)
def getMatchedCmdsWithGrade(refCode,tarCode):
    res = myutils.iff(lambda x: x=="",refCode,tarCode)
    if res==1:
        return {'matchedCmds':[],'deletedCmds':[],'insertedCmds':[],'gradesDict':{'ratio':100,'contain':100},'refCode':refCode,'tarCode':tarCode}
    if res==0:
        refCmds = refCode.split(";")
        tarCmds = tarCode.split(";")
        (matchedCmds,deletedCmds,insertedCmds,grade) = __doGetMatchedCmds(refCmds,tarCmds)
        return {'matchedCmds':matchedCmds,'deletedCmds':deletedCmds,'insertedCmds':insertedCmds,'gradesDict':__getGradesDict(grade, refCmds, tarCmds),'refCode':refCode,'tarCode':tarCode}
    else:
        return {'matchedCmds':[],'deletedCmds':[],'insertedCmds':[],'gradesDict':{'ratio':0,'contain':0},'refCode':refCode,'tarCode':tarCode}
      

def compareDisAsmCode(refCode,tarCode):
    res = myutils.iff(lambda x: x=="",refCode,tarCode)
    if res==1:
        return {'ratio':100,'contain':100}
    
    if res==0:
        refCmds = refCode.split(";")
        tarCmds = tarCode.split(";")
        grade = __doGetMatchedCmds(refCmds,tarCmds,False)
        return __getGradesDict(grade, refCmds, tarCmds)
    else:
        return {'ratio':0,'contain':0}
    
    

# this will return compare methods in order of precition, from less to most (presice)
def getCompareMethods():
    yield compareDisAsmCode 
    
