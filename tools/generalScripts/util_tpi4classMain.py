#########################################################################################
## Script name:     tpi4classMain.py
## Command line:    tpi4class
## ArcGIS Version:  9.1
## Last modified:   25 January 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates topographic position index with 4 classes - gentle slopes,
##                  steep slopes, ridgetops, and canyonbottoms
## Parameter List:
##                  Argv[1]     Project Workspace  
##                  Argv[2]     Elevation raster
##                  Argv[3]     tpiNeighborhood
##                  Argv[4]     canyonsThreshold
##                  Argv[5]     ridgesThreshold
##                  Argv[6]     slopesThreshold
##                  Argv[7]     deleteTpiGrid
#########################################################################################                                                               # Import system modules
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions, util_tpi4classModule

# CALL FUNCTIONS -------------------------------------------------------------------------------  
# Arguments ------------------------------#####
try:
    elevationGrid = sys.argv[1]
    outputTpi = sys.argv[2]    
    tpiNeighborhood = sys.argv[3]
    canyonsThreshold = sys.argv[4]
    ridgesThreshold = sys.argv[5]
    slopesThreshold = sys.argv[6]
    deleteTpiGrid = sys.argv[7]

    toolName = 'createTPI'
    inParameters = "%s %s '%s' %s %s %s %s" % (elevationGrid,
                                             outputTpi,
                                             tpiNeighborhood,
                                             canyonsThreshold,
                                             ridgesThreshold,
                                             slopesThreshold,
                                             deleteTpiGrid)


# Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    gp.Extent = desc(elevationGrid).Extent
    userWorkspace = os.path.dirname(outputTpi)
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/") + '/'
    except:
        workspace = userWorkspace
    totalSteps = '4'
    logFile = createLogFile(workspace, toolName, inParameters)
    
# Call functions ------------------------------#####    
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: CreateTPI') 
    gp.AddMessage('')
    
    try:
        gp.AddMessage (' Step 1/'+totalSteps+') Deriving slope')
        slopeOutput = util_tpi4classModule.deriveSlope(gp, workspace, elevationGrid)
        gp.AddMessage (' Step 2/'+totalSteps+') Creating topographic position index grid')        
        tpiGrid = util_tpi4classModule.createTpiGrid(gp, workspace, elevationGrid, tpiNeighborhood)
        gp.AddMessage (' Step 3/'+totalSteps+') Creating topographic slope position grid')
        topoPosition = util_tpi4classModule.createSlopePositionGrid(gp, outputTpi, workspace, tpiGrid, slopeOutput, canyonsThreshold,
                                                         ridgesThreshold, slopesThreshold, deleteTpiGrid)
        gp.delete(slopeOutput)
        gp.AddMessage(' Finished! ')
        gp.AddMessage('  ')
        closeLogFile(logFile)
        del gp
    except:
        addErrorMessages(gp)
        closeLogFile(logFile)
        del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp

