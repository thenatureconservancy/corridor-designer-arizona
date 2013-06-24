#########################################################################################
## Script name:     hab_modifyHsmCriticalFactor.py
## Command line:    reclassifyUnsuitableFeatures
## ArcGIS Version:  9.1
## Last modified:   16 July 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Reclassifies HSM according to distance from critical feature
##                   
## Parameter List:
##                  Argv[1]    Input HSM
##                  Argv[2]    Output reclassified HSM
##                  Argv[3]    Critical feature
##                  Argv[4]    Reclassification range
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#---------------------------------------------------------------------------------------
# 3. Multiply reclass grid by HSM
def reclassDistanceRange(inputHsm, outputHsm, criticalFactor, reclassRange):
    gp.AddMessage(' Step 1/'+totalSteps+') Calculating distance to critical feature grid')
    distanceToCriticalFeature = workspace + '/dstCrtFact'
    gp.EucDistance_sa (criticalFactor, distanceToCriticalFeature, "999999", inputHsm)
    gp.AddMessage(' Step 2/'+totalSteps+') Reclassifying distance to critical feature grid')
    reclassCriticalFeature = workspace + '/rclsCritFact'    
    gp.Reclassify_sa(distanceToCriticalFeature, "Value", reclassRange, reclassCriticalFeature, "DATA")
    gp.AddMessage(' Step 3/'+totalSteps+') Multiplying reclassed distance grid by HSM')
    timesRaster = workspace + '/timesGrid'    
    gp.Times_sa(inputHsm, reclassCriticalFeature, timesRaster)
    gp.AddMessage(' Step 4/'+totalSteps+') Calculating new HSM')   
    timesRaster = workspace + '/timesGrid'    
    gp.Divide_sa(timesRaster, '100', outputHsm)   
    gp.delete (distanceToCriticalFeature)
    gp.delete (reclassCriticalFeature)
    gp.delete (timesRaster)  
    return outputHsm

# Script arguments ------------------------------#####
try:
    inputHsm = sys.argv[1]
    criticalFactor = sys.argv[2]    
    outputHsm = sys.argv[3]
    reclassRange = sys.argv[4]

    toolName = 'CriticalFeature'
    inParameters = "%s %s %s '%s'" % (inputHsm,
                                    criticalFactor,
                                    outputHsm,                                    
                                    reclassRange)


    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1 
    userWorkspace = os.path.dirname(outputHsm)
    desc = gp.Describe
    gp.Extent = desc(inputHsm).Extent
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    totalSteps = '4'
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: CriticalFeature') 
    gp.AddMessage('')
   
    newHsm = reclassDistanceRange(inputHsm, outputHsm, criticalFactor, reclassRange)

    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp