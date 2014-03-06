#!/usr/bin/python

import os
import commands
import time
import sys
import time

from sendMail import sendMail

#name of process to look for
procnamePrefix = "findClone"

waitStart = False
waitEnd = True

while True:
    output = commands.getoutput("ps -A")
    found = False
    for process in output.split("\n"):
        if "<defunct>" in process:
            sendMail("Zombies!!! call rick!!!")
            while True:
                pass
        if procnamePrefix in process:
            #print "FOUND!"
            found = True
    
    if found == False:
        if waitEnd:
            #ok we stopped, alert via main and toggle
            sendMail("Watch dog exit")
            waitStart = True
            waitEnd = False
            print "Waiting for start"
    else:
        if waitStart:
            # ok we have start...toggle
            waitStart = False
            waitEnd = True
            print "Waiting for END"
    
    # sleep 5 mins
    time.sleep(60*5)

