#########################################################################################
## Script name:     unionAndDissolveCorridors.py
## Command line:    UnionCorridors
## ArcGIS Version:  9.1
## Last modified:   23 March 2006
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Unions and dissolves user-input corridors or polygons
##                   
## Parameter List:
##                  Argv[1] Output Name
##                  Argv[2] Corridors to Union
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

def unionAndDissolve():
    try:
        unionOutput =workspace + '/corridor_union.shp'
        gp.AddMessage ('            - Creating union of corridors')        
        gp.union_analysis(inputFeatures, unionOutput, "ALL", "", "GAPS")
        gp.AddMessage ('            - Dissolving union of corridors')
        gp.Dissolve_management(unionOutput, outputShapefile, "", "", "MULTI_PART")    
        gp.delete(unionOutput)
        return outputShapefile
    except:
        addErrorMessages(gp)         

# CALL FUNCTIONS -------------------------------------------------------------------------------
try:
    # Script arguments ------------------------------#####
    inputFeatures = sys.argv[1]
    outputShapefile = sys.argv[2]

    desc = gp.Describe    
    userWorkspace = os.path.dirname(outputShapefile)
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    totalSteps = '1'

    toolName = 'UnionCorridors'
    inParameters = '%s %s' % (inputFeatures,
                              outputShapefile
                              )    
    
    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1
    logFile = createLogFile(workspace, toolName, inParameters)
    
    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: UnionCorridors') 
    gp.AddMessage('')
    gp.AddMessage(' Step 1/'+totalSteps+') Creating union of corridors')
    unionAndDissolve()
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
    
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp