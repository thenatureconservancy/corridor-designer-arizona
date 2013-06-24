#########################################################################################
## Script name:     util_prepareWorkspaceAZ.py
## Command line:    prepareWorkspaceAZ
## ArcGIS Version:  wrote with 9.1, should work with 9.2
## Last modified:   04 April 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates workspace for AZ Toolbox. Clips land cover & elevation;
##                  clips roads and creates distance-from-roads grid; creates
##                  topographic slope position layer; clips any additional feature
##                  classes or rasters
##                   
## Parameter List:
##                  Argv[1]     Project Workspace
##                  Argv[2]     Feature used for clipping
##                  Argv[3]     Land cover raster    
##                  Argv[4]     Elevation raster
##                  Argv[5]     Roads feature class
##                  Argv[6]     tpiNeighborhood
##                  Argv[7]     canyonsThreshold
##                  Argv[8]     ridgesThreshold
##                  Argv[9]     slopesThreshold
##                  Argv[10]    deleteTpiGrid
##                  Argv[11]    featureList
##                  Argv[12]    rasterList
##
#########################################################################################
import sys, string, os, time
sys.path.append(os.path.split(os.path.dirname(sys.argv[0]))[0] +'/generalScripts')
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions, util_tpi4classModule

#----------------------------------------------------------------------------------------
def createDirectories(workspace):
    try:
        try:
            os.mkdir(workspace)
            gp.AddMessage(' Step 1/'+totalSteps+') Created basemap directory for project')
        except:
            gp.AddMessage(' Step 1/'+totalSteps+') Basemap directory already exists for project')        
        try:
            os.mkdir(outputDir)
            gp.AddMessage(' Step 2/'+totalSteps+') Created output directory for project')
        except:
            gp.AddMessage(' Step 2/'+totalSteps+') Output directory already exists for project')
    except:
        addErrorMessages(gp)      
#----------------------------------------------------------------------------------------
def createDstRoads():
    try:
        gp.AddMessage (' Step 4/'+totalSteps+') Clipping roads feature class...')
        roadsClipOutput = workspace + 'roads.shp' #have to leave .shp extension, otherwise script can't find layer
        gp.Clip_analysis(roadsFc, clipFeature, roadsClipOutput,"")
        gp.AddMessage (' Step 5/'+totalSteps+') Creating distance-from-roads grid...')        
        distanceToRoadsRaster = workspace  + 'dstroad'
        gp.EucDistance_sa (roadsClipOutput, distanceToRoadsRaster, '', landcover, '')
        return distanceToRoadsRaster
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------
# Might need to change back to short names, e.g. veg, road,
# topo, elev...depending on how tabs in text file/cursor work

def clipLandcover(workspace, landcover, clipFeature):
    try:
        gp.AddMessage (' Step 3/'+totalSteps+') Clipping land cover grid...')
        landcoverClipOutput = workspace + 'lndcvr'     
        gp.ExtractByMask_sa(landcover, clipFeature, landcoverClipOutput)
        return landcoverClipOutput
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------
def clipElevation():
    try:
        gp.AddMessage (' Step 6/'+totalSteps+') Clipping elevation grid...')
        elevationClipOutput = workspace + 'elev_m'
        gp.ExtractByMask_sa(elevation, clipFeature, elevationClipOutput)
        return elevationClipOutput
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------
def clipFeatures(workspace, featureList):
    try:
        gp.AddMessage (' Step 8/'+totalSteps+') Clipping feature classes...')        
        splitFeatures = featureList.split(';')
        for feature in splitFeatures:
            gp.AddMessage ('            -clipping '+ feature + ' ...')
            clipOutput = workspace  + os.path.basename(feature) 
            gp.Clip_analysis(feature, clipFeature, clipOutput,"")
        gp.AddMessage('            -finished clipping all feature classes')
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------   
def clipRasters(workspace, rasterList):
    try:
        gp.AddMessage (' Step 9/'+totalSteps+') Clipping rasters...')
        splitRasters = rasterList.split(';')
        for raster in splitRasters:
            gp.AddMessage ('            -clipping '+ raster + ' ...')
            clipOutput = workspace  + os.path.basename(raster)
            gp.ExtractByMask_sa(raster, clipFeature, clipOutput)
        gp.AddMessage ('            -finished clipping all rasters')
    except:
        addErrorMessages(gp)

# Call Functions-------------------------------------------------------------------------
# Arguments ------------------------------#####
try:
    clipFeature = sys.argv[1]    
    userWorkspace = sys.argv[2]
    roadsFc = sys.argv[3]    
    landcover = sys.argv[4]
    elevation = sys.argv[5]
    tpiNeighborhood = sys.argv[6]
    canyonsThreshold = sys.argv[7]
    ridgesThreshold = sys.argv[8]
    slopesThreshold = sys.argv[9]
    deleteTpiGrid = sys.argv[10]
    featureList = sys.argv[11]
    rasterList = sys.argv[12]
    
    toolName = 'PrepareWorkspaceAZ'
    inParameters = "%s %s %s %s %s '%s' %s %s %s %s %s %s" %(clipFeature,
                                                           userWorkspace,
                                                             roadsFc,
                                                           landcover,
                                                           elevation,
                                                           tpiNeighborhood,
                                                           canyonsThreshold,
                                                           ridgesThreshold,
                                                           slopesThreshold,
                                                           deleteTpiGrid,
                                                           featureList,
                                                           rasterList)
    

# Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    gp.Extent = desc(clipFeature).Extent
    try:
        outputDir = desc(userWorkspace).CatalogPath.replace("\\","/") + '/output/'
    except:
        outputDir = userWorkspace + '/output/'
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/") + '/basemap/'
    except:
        workspace = userWorkspace + '/basemap/'
    totalSteps = '9'
    if featureList == '#' and rasterList == '#':
        totalSteps = '7'
    elif featureList == '#':
        totalSteps = '8'
    elif rasterList =='#':
        totalSteps = '8'
    else:
        totalSteps = '9'

# Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: PrepareWorkspaceAZ') 
    gp.AddMessage('')
    
    createDirectories(workspace)
    logFile = createLogFile(workspace, toolName, inParameters)
    clippedLandcover = clipLandcover(workspace, landcover, clipFeature)
    dstRoads = createDstRoads()    
    elevationClip = clipElevation()

    # Create Topo layer (TPI & Slope position)
    try:
        gp.AddMessage (' Step 7/'+totalSteps+') Creating topographic position grid')
        slopeOutput = util_tpi4classModule.deriveSlope(gp, workspace, elevationClip)
        tpiGrid = util_tpi4classModule.createTpiGrid(gp, workspace, elevationClip, tpiNeighborhood)
        outputTpi = workspace + 'topo' 
        topoPosition = util_tpi4classModule.createSlopePositionGrid(gp, outputTpi, workspace, tpiGrid, slopeOutput, canyonsThreshold,
                                                         ridgesThreshold, slopesThreshold, deleteTpiGrid)
    except:
        addErrorMessages(gp)
        closeLogFile(logFile)
        del gp

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
