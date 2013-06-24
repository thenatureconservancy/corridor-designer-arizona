#########################################################################################
## Script name:     hab_reclassifyUnsuitableFeatures.py
## Command line:    reclassifyUnsuitableFeatures
## ArcGIS Version:  9.1
## Last modified:   19 April 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Reclassifies unsuitable features
##                   
## Parameter List:
##                  Argv[1]    Input HSM
##                  Argv[2]    Output Reclassified HSM
##                  Argv[3]    Vector Layers
##                  Argv[4]    Raster Layers
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#---------------------------------------------------------------------------------------
def featureToRaster():
    reclassRaster = workspace + '/tmpRaster1'
    gp.ExtractByMask_sa(inputHsm, reclassFeature, reclassRaster)
    return reclassRaster

def reclassifyRaster(inputHsm, reclassRaster, reclassScore, outputHsm):
    try:
        print 'reclassifing raster so NoData has a value of 0'
        # Reclassify raster so NoData has a value of 0. Otherwise Con statement won't work
        reclassedRaster = workspace + '/tmpRaster2'
        gp.Reclassify_sa(reclassRaster, "Value", "-999 999999 1; NoData 0", reclassedRaster)
        # Con statement: if
        print 'using con statement'
        gp.Con_sa(reclassedRaster, reclassScore, outputHsm, inputHsm, "value > 0")
        gp.delete(reclassRaster)
        gp.delete(reclassedRaster)
        return outputHsm
    except:
        addErrorMessages(gp)        

# Script arguments ------------------------------#####
try:
    inputHsm = sys.argv[1]
    reclassFeature = sys.argv[2]    
    outputHsm = sys.argv[3]
    reclassScore = sys.argv[4]

    toolName = 'ReclassifyFeatures'
    inParameters = '%s %s %s %s' % (inputHsm,
                                    reclassFeature,
                                    outputHsm,
                                    reclassScore)

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
    totalSteps = '2'
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: ReclassifyFeatures') 
    gp.AddMessage('')

    gp.AddMessage(' Step 1/'+totalSteps+') Masking out reclassified features')
    reclassRaster = featureToRaster()
    gp.AddMessage(' Step 2/'+totalSteps+') Reclassifying HSM')
    outRaster = reclassifyRaster(inputHsm, reclassRaster, reclassScore, outputHsm)
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp