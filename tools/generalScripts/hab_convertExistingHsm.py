#########################################################################################
## Script name:     convertExistingHsm.py
## Command line:    normalizeExistingHsm
## ArcGIS Version:  9.1
## Last modified:   09 April 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Converts existing HSM to 0-100 scale
##                   
## Parameter List:
##                  Argv[1]    Existing HSM
##                  Argv[2]    Output HSM
##                  Argv[3]    Method to convert HSM
##                  Argv[4]    Worst habitat value
##                  Argv[5]    Best habitat value
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#----------------------------------------------------------------------------------------
def stretchHsm(inputHsm, worstHabitatValue, bestHabitatValue, outputHsm):
    #stretchHsm = workspace + '/hsm_stretched'
    #roundedHsm = workspace + '/hsm_rounded'
    inExpression = '((' +inputHsm+ ' - ' +worstHabitatValue+ ') / (' +bestHabitatValue+ ' - ' +worstHabitatValue+ ')) * 100'
    gp.AddMessage(' Step 1/1) Stretching HSM to 0-100 range')
    gp.SingleOutputMapAlgebra_sa(inExpression, outputHsm)
##    gp.AddMessage(' Step 2/4) Rounding up stretched HSM')
##    gp.RoundUp_sa(stretchHsm, roundedHsm)
##    gp.AddMessage(' Step 2/3) Converting HSM to integer')    
##    gp.Int_sa(stretchHsm, outputHsm)
##    gp.AddMessage(' Step 3/3) Deleting temp layers')    
##    gp.Delete(stretchHsm)
##    gp.Delete(roundedHsm)
    return outputHsm

# CALL FUNCTIONS ---------------------------------------------------------------------------
try:
    # Script arguments ------------------------------#####
    inputHsm = sys.argv[1]
    outputHsm = sys.argv[2]
    worstHabitatValue = sys.argv[3]
    bestHabitatValue = sys.argv[4]

    toolName = 'NormalizeExistingHSM'
    inParameters = '%s %s %s %s' % (inputHsm,
                                    outputHsm,
                                    worstHabitatValue,
                                    bestHabitatValue)

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    userWorkspace = os.path.dirname(inputHsm)
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    gp.Extent = desc(inputHsm).Extent
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: normalizeExistingHsm') 
    gp.AddMessage('')

    if int(bestHabitatValue) != int(worstHabitatValue):
        stretchedHsm = stretchHsm(inputHsm, worstHabitatValue, bestHabitatValue, outputHsm)
        gp.AddMessage(' Finished! ')
        gp.AddMessage('  ')
        closeLogFile(logFile)
        del gp

    elif bestHabitatValue == worstHabitatValue:
        gp.AddMessage('')
        gp.AddMessage(' WARNING: You set values for worst and best habitat equal!')
        gp.AddMessage('')
        closeLogFile(logFile)
        del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp

        