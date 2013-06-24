#########################################################################################
## Script name:     gen_logFile.py
## Command line:    none - module only; called by various tools
## ArcGIS Version:  9.1
## Last modified:   21 July 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Functions to aid in log file creation
##                   
## Parameter List:
##
#########################################################################################
import time, sys, os, string
    
#Create text file for species
def createLogFile(workspace, toolName, inParameters):
    ft = tuple(time.localtime())
    timeNow = time.ctime()
    try:
        logFile=open(workspace + '/%s_%s_%s_%s%s_%s.txt' % (ft[0], ft[1], ft[2], ft[3], ft[4], toolName),'a')
    except:
        logFile=open(workspace + '/%s_%s_%s_%s%s_%s.txt' % (ft[0], ft[1], ft[2], ft[3], ft[4], toolName),'w')
    logFile.write('*'*70 + '\n')
    logFile.write('CORRIDORDESIGNER LOG FILE: %s \n\n' % (toolName))
    logFile.write('Start time:\t\t%s \n' % (timeNow))
    logFile.write('Command line syntax:\t%s %s \n\n' % (toolName, inParameters))
    return logFile

def lfw(logFile, inString):
    logFile.write(inString + '\n')
    
def closeLogFile(logFile):
    timeNow = time.ctime()
    logFile.write('Stop time:\t\t%s \n\n' % (timeNow))    
    logFile.close()

# Testing input
##workspace = "C:/GIS/CorridorDesigner"
##toolName = "brodeo"
##inParameters = '''
##    workspace +
##    toolName
##    '''
##
##logFile = createLogFile(workspace, toolName, inParameters)
#closeLogFile()