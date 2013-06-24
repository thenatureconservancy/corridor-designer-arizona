#########################################################################################
## Script name:     clipLayers.py
## Command line:    clipAnalysisLayers
## ArcGIS Version:  wrote with 9.1, should work with 9.2
## Last modified:   07 March 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Clips all feature classes or rasters
##                   
## Parameter List:
##                  Argv[1]     User Workspace where clipped layers will go
##                  Argv[2]     Feature used for clipping 
##                  Argv[3]     List of feature classes
##                  Argv[4]     List of rasters
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#----------------------------------------------------------------------------------------
def clipFeatures(workspace, featureList):
    try:
        gp.AddMessage (' Step 1/'+totalSteps+') Clipping feature classes...')        
        splitFeatures = featureList.split(';')
        for feature in splitFeatures:
            try:               
                gp.AddMessage ('            -clipping '+ feature + '...')
                clipOutput = workspace  + os.path.basename(feature)
                gp.Clip_analysis(feature, clipFeature, clipOutput,"")
            except:
                gp.AddMessage ('            -WARNING: could not clip '+ feature)
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------   
def clipRasters(workspace, rasterList):
    try:
        gp.AddMessage (' Step 2/'+totalSteps+') Clipping rasters...')
        splitRasters = rasterList.split(';')
        for raster in splitRasters:
            try:
                gp.AddMessage ('            -clipping '+ raster + '...')
                clipOutput = workspace  + os.path.basename(raster)
                gp.ExtractByMask_sa(raster, clipFeature, clipOutput)
            except:
                gp.AddMessage ('            -WARNING: could not clip '+ raster)
    except:
        addErrorMessages(gp)

# Call Functions-------------------------------------------------------------------------
# Arguments ------------------------------#####
try:
    clipFeature = sys.argv[1]
    userWorkspace = sys.argv[2]
    featureList = sys.argv[3]
    rasterList = sys.argv[4]

    toolName = 'ClipAnalysisLayers'
    inParameters = '%s %s %s %s' % (clipFeature,
                                    userWorkspace,
                                    featureList,
                                    rasterList)

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    gp.Extent = desc(clipFeature).Extent
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/") + '/'
    except:
        workspace = userWorkspace
    totalSteps = '2'
    logFile = createLogFile(workspace, toolName, inParameters)
    
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: ClipAnalysisLayers') 
    gp.AddMessage('')

    # Call functions ------------------------------#####
    if featureList =="#":
        print 'no features to clip'
    else:
        clipFeatures(workspace, featureList)
    if rasterList =="#":
        print 'no rasters to clip'
    else:        
        clipRasters(workspace, rasterList)

    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp
  



