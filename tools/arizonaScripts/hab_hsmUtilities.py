# Script name:     hsmUtilities.py                          
# Command line:    none; called by hsiMain                      
# ArcGIS Version:  9.1                                          
# Last modified:   19 December 2006                             
# Author:          Dan Majka (dan@corridordesign.org)           
# Description:     Utility functions used by hsmMain       
# ---------------------------------------------------------------
import os, sys, time, string

#----------------------------------------------------------------------------------------
def checkSpecDirPath(gp):
    installDir = os.path.dirname(sys.argv[0])
    specTextFile = installDir + '/speciesDirectoryPath.txt'
    specDirPathString = installDir + '/species/'
    try:
        specDirPath = open(specTextFile,'r')
        specDirPathString = specDirPath.readline()
        specDirPath.close()
    except:
        try:
##            gp.AddMessage(' - No speciesDirectoryPath.txt file exists...creating one')
            specDirPath = open(specTextFile,'w')
            specDirPath.write(specDirPathString)
            specDirPath.close()
        except:
            gp.AddMessage('''
*****************************************************************
STOPPING: CorridorDesigner needs permission to write to the path:
'''+installDir+ '.' + '''
*****************************************************************''')
        
    if os.path.exists(specDirPathString):
        print ('the path exists')
##        gp.AddMessage('the path exists...continuing')#Remove this when finished testing.
    else:
        gp.AddMessage('''
*****************************************************************
STOPPING: The folder containing species parameters
is not in its default location. Please use the "Set Species
Path" tool in the Prepare Layers toolbox to define
a new path for your species parameterizations, or move the
species folder back into the install folder, whose path is:
'''+installDir+ '.' + '''
*****************************************************************''')
    return specDirPathString

#----------------------------------------------------------------------------------------
def createOutputFolder (workspace, specName, speciesFullName, gp):
    try:
        os.mkdir(workspace+'/output/')
        print('Created output directory for project')
    except:
        print('Output directory already exists for project')
    try:
        specFolder = os.mkdir(workspace+'/output/'+specName)
        gp.AddMessage('            -created directory for '+speciesFullName+ ' in: '+workspace+'/output/')
        return specFolder
    except:
        gp.AddMessage('            -directory already exists for '+speciesFullName+ ' in: '+workspace+'/output/')
        specFolder = (workspace+'/output/'+specName)
        return specFolder
#----------------------------------------------------------------------------------------
def createLogFile (workspace, specName):
    # Create text file file for species
    try:
        logFile=open(workspace+ '/' +specName+ '/_' +specName+ '_log.txt','a')
    except:
        logFile=open(workspace+ '/' +specName+ '/_' +specName+ '_log.txt','w')
      
    # Get current time and write to text file
    time1=time.localtime()
    time2=time.asctime(time1)
    logFile.write(''+'\n\n')
    logFile.write(''+'\n\n')
    logFile.write('Start time: '+time2+'\n\n')
    logFile.write('\n')
    logFilet.write('\n')
    logFile.write('\n\n')
    return logFile

