#########################################################################################
## Script name:     fillHolesInCorridors.py
## Command line:    fillCorridorHoles
## ArcGIS Version:  9.1
## Last modified:   29 January 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Fills holes in corridor feature class
##                   
## Parameter List:
##                  Argv[1]    Corridor shapefile
##                  Argv[2]    Output Buffered shapefile
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#----------------------------------------------------------------------------------------
def fillHoles(inputCorridor, holeDistance, outputCorridor, workspace):
    try:
        bufferedCorridor = workspace + '/_bufferedCorridor.shp'
        bufferDistance = int(holeDistance)/2
        negBufferDistance = -(bufferDistance)
        gp.Buffer_analysis(inputCorridor, bufferedCorridor, bufferDistance, '', '', 'ALL', '')
        print(' - buffered corridor')
        gp.Buffer_analysis(bufferedCorridor, outputCorridor, negBufferDistance, '', '', 'ALL', '')
        print(' - negative buffer')
        gp.delete(bufferedCorridor)
        return outputCorridor
    except:
        addErrorMessages(gp)        

# CALL FUNCTIONS -------------------------------------------------------------------------------
# Script arguments
try:
    # Script arguments ------------------------------#####    
    inputCorridor = sys.argv[1]
    outputCorridor = sys.argv[2]    
    holeDistance = sys.argv[3]

    toolName = 'FillCorridorHoles'
    inParameters = '%s %s %s' % (inputCorridor,
                                 outputCorridor,
                                 holeDistance
                                 )    
    
    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    userWorkspace = os.path.dirname(outputCorridor)
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    totalSteps = '1'
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: sliceCorridor') 
    gp.AddMessage('')
    gp.AddMessage(' Step 1/'+totalSteps+') Filling all holes less than ' +holeDistance+ ' map units wide')
    fillHoles(inputCorridor, holeDistance, outputCorridor, workspace)
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp
